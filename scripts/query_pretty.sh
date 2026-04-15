#!/usr/bin/env bash

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 \"<question>\" [session_id]"
  exit 1
fi

QUESTION="$1"
SESSION_ID="${2:-terminal-demo}"
WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:5678/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat}"

PAYLOAD=$(python3 - "$QUESTION" "$SESSION_ID" <<'PY'
import json
import sys

question = sys.argv[1]
session_id = sys.argv[2]
print(json.dumps({
    "action": "sendMessage",
    "chatInput": question,
    "sessionId": session_id,
}, ensure_ascii=False))
PY
)

RAW=$(curl -sS --max-time 180 \
  -H "Content-Type: application/json" \
  -X POST "$WEBHOOK_URL" \
  -d "$PAYLOAD" \
  -w $'\n__HTTP_CODE__:%{http_code}\n__TIME_TOTAL__:%{time_total}\n')

HTTP_CODE=$(printf '%s\n' "$RAW" | awk -F: '/^__HTTP_CODE__/{print $2}')
TIME_TOTAL=$(printf '%s\n' "$RAW" | awk -F: '/^__TIME_TOTAL__/{print $2}')
BODY=$(printf '%s\n' "$RAW" | sed '/^__HTTP_CODE__:/,$d')

python3 - "$BODY" "$HTTP_CODE" "$TIME_TOTAL" <<'PY'
import json
import re
import sys
import textwrap

body = sys.argv[1]
http_code = sys.argv[2]
time_total = sys.argv[3]

def clean_text(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "(пустой ответ)"

    # Preferred path: model returns strict JSON like {"answer":"..."}.
    try:
        obj = json.loads(t)
        if isinstance(obj, dict) and isinstance(obj.get("answer"), str) and obj["answer"].strip():
            return obj["answer"].strip()
    except Exception:
        pass

    # If model returns chain-of-thought blocks, try to extract final section.
    if re.match(r"(?is)^\s*thinking process\s*:", t):
        extracted = None
        for marker in [
            "Final Answer:",
            "Final Output:",
            "Итоговый ответ:",
            "Ответ:",
        ]:
            idx = t.lower().find(marker.lower())
            if idx != -1:
                extracted = t[idx + len(marker):].strip()
                break
        if extracted:
            t = extracted
        else:
            return (
                "Модель вернула служебные рассуждения без финального ответа. "
                "Повторите запрос или перезапустите workflow."
            )

    # Compact extra whitespace.
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t or "(пустой ответ)"

try:
    data = json.loads(body)
except json.JSONDecodeError:
    print("=== RESPONSE ===")
    print(body.strip() or "(пусто)")
    print(f"\nHTTP: {http_code} | Time: {time_total}s")
    sys.exit(0)

text = ""
if isinstance(data, dict):
    if isinstance(data.get("response"), dict):
        text = data["response"].get("text", "")
    if not text and isinstance(data.get("output"), str):
        text = data["output"]

cleaned = clean_text(text)
wrapped = textwrap.fill(cleaned, width=100, replace_whitespace=False)

print("=== RAG ANSWER ===")
print(wrapped)
print(f"\nHTTP: {http_code} | Time: {time_total}s")
PY
