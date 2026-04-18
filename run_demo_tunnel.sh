#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="${PROJECT_NAME:-finreg}"
N8N_PORT="${N8N_PORT:-5678}"
N8N_URL="${N8N_URL:-http://localhost:${N8N_PORT}}"
N8N_HEALTH_URL="${N8N_HEALTH_URL:-${N8N_URL}/healthz}"
QUERY_WORKFLOW_FILE="${QUERY_WORKFLOW_FILE:-${ROOT_DIR}/n8n/query_workflow.json}"
DEFAULT_WEBHOOK_ID="62eb0006-34f6-4d09-987e-edf71ca0b255"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: '$cmd' not found."
    if [[ "$cmd" == "cloudflared" ]]; then
      echo "Install on macOS: brew install cloudflared"
    fi
    exit 1
  fi
}

extract_url() {
  local file="$1"
  if command -v rg >/dev/null 2>&1; then
    rg -o "https://[a-z0-9-]+\\.trycloudflare\\.com" "$file" | head -n 1 || true
  else
    grep -Eo "https://[a-z0-9-]+\\.trycloudflare\\.com" "$file" | head -n 1 || true
  fi
}

resolve_webhook_id() {
  local webhook_id="$DEFAULT_WEBHOOK_ID"
  if command -v jq >/dev/null 2>&1 && [[ -f "$QUERY_WORKFLOW_FILE" ]]; then
    local detected
    detected="$(jq -r '.[0].nodes[]? | select(.name=="When chat message received") | .webhookId // empty' "$QUERY_WORKFLOW_FILE" 2>/dev/null || true)"
    if [[ -n "$detected" && "$detected" != "null" ]]; then
      webhook_id="$detected"
    fi
  fi
  echo "$webhook_id"
}

require_cmd docker
require_cmd curl
require_cmd cloudflared

WEBHOOK_ID="$(resolve_webhook_id)"
LOG_FILE="$(mktemp -t finreg-trycloudflare-XXXX.log)"
CF_PID=""

cleanup() {
  if [[ -n "$CF_PID" ]] && kill -0 "$CF_PID" >/dev/null 2>&1; then
    kill "$CF_PID" >/dev/null 2>&1 || true
    wait "$CF_PID" 2>/dev/null || true
  fi
  rm -f "$LOG_FILE"
}

trap cleanup EXIT INT TERM

echo "[1/4] Starting services with docker compose..."
docker compose -p "$PROJECT_NAME" up -d

echo "[2/4] Waiting for n8n health endpoint..."
READY=0
for _ in $(seq 1 90); do
  if curl -fsS "$N8N_HEALTH_URL" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [[ "$READY" -ne 1 ]]; then
  echo "Error: n8n is not healthy at $N8N_HEALTH_URL"
  exit 1
fi

echo "[3/4] Starting Cloudflare Quick Tunnel..."
cloudflared tunnel --url "$N8N_URL" --no-autoupdate >"$LOG_FILE" 2>&1 &
CF_PID="$!"

PUBLIC_URL=""
for _ in $(seq 1 90); do
  if ! kill -0 "$CF_PID" >/dev/null 2>&1; then
    echo "Error: cloudflared exited unexpectedly."
    echo "cloudflared log:"
    sed -n '1,160p' "$LOG_FILE"
    exit 1
  fi
  PUBLIC_URL="$(extract_url "$LOG_FILE")"
  if [[ -n "$PUBLIC_URL" ]]; then
    break
  fi
  sleep 1
done

if [[ -z "$PUBLIC_URL" ]]; then
  echo "Error: failed to obtain trycloudflare URL within timeout."
  echo "cloudflared log:"
  sed -n '1,160p' "$LOG_FILE"
  exit 1
fi

UI_URL="${PUBLIC_URL}/home/workflows"
WEBHOOK_URL="${PUBLIC_URL}/webhook/${WEBHOOK_ID}/chat"

echo "[4/4] Demo links are ready:"
echo
echo "n8n UI:      $UI_URL"
echo "Chat webhook: $WEBHOOK_URL"
echo
echo "Test command:"
cat <<EOF
curl -sS -X POST "$WEBHOOK_URL" \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "sendMessage",
    "chatInput": "Какой статус у компании ТОО \\"НурТех Групп\\"?",
    "sessionId": "manager-test"
  }'
EOF
echo
echo "Tunnel is active while this terminal is running. Press Ctrl+C to stop."

wait "$CF_PID"
