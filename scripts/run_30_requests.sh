#!/usr/bin/env bash
set -euo pipefail

WEBHOOK="${WEBHOOK:-http://localhost:5678/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat}"
MAX_REQUESTS="${MAX_REQUESTS:-0}"

queries=(
  '/fast Дельта Плюс Павлодар'
  '/fast Альянс Групп Алматы'
  '/fast Гранит Трейд Астана'
  '/fast Какой статус у компании АО "Дельта Плюс"?'
  '/fast Когда зарегистрирована компания ИП "Альянс Групп"?'
  '/fast Чем занимается компания АО "Гранит Трейд"?'
  '/fast Сколько активных компаний в Павлодаре?'
  '/fast Найди активные компании в Алматы'
  '/fast Чем занимается компания Альянс?'
  '/fast Какая выручка у АО "Дельта Плюс" за 2025 год?'
  '/fast Кто владелец ИП "Альянс Групп"?'
  '/fast Сколько ликвидированных компаний в Астане?'
  '/fast Найди компании в Астане'
  '/fast Покажи компании в Караганде'
  '/fast Какой статус у компании ИП "ЭкоГрупп"?'
  '/rag Дельта Плюс Павлодар'
  '/rag Альянс Групп Алматы'
  '/rag Чем занимается компания ИП "Альянс Групп"?'
  '/rag Какой статус у компании АО "Гранит Трейд"?'
  '/rag Сколько активных компаний в Павлодаре?'
  '/rag Найди компании, похожие на IT-сферу в Алматы'
  '/rag Что есть по теме обслуживания оборудования в Астане?'
  '/rag Найди технологические компании в Павлодаре'
  '/rag Покажи компании про логистику в Алматы'
  '/rag Чем занимается компания Альянс?'
  '/rag Кто владелец АО "Дельта Плюс"?'
  '/rag Какая выручка у АО "Дельта Плюс" за 2025 год?'
  '/mode fast Дельта Плюс Павлодар'
  '/mode rag Чем занимается компания ИП "Альянс Групп"?'
  'Гранит Трейд Астана'
)

idx=1
for q in "${queries[@]}"; do
  if [[ "$MAX_REQUESTS" =~ ^[0-9]+$ ]] && [ "$MAX_REQUESTS" -gt 0 ] && [ "$idx" -gt "$MAX_REQUESTS" ]; then
    break
  fi

  sid=$(printf 'demo-%02d' "$idx")
  echo "[$sid] $q"

  payload=$(python3 - "$q" "$sid" <<'PY'
import json
import sys

query = sys.argv[1]
sid = sys.argv[2]
print(json.dumps({
    "action": "sendMessage",
    "chatInput": query,
    "sessionId": sid,
}, ensure_ascii=False))
PY
)

  curl -sS -X POST "$WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "$payload"
  echo
  echo

  idx=$((idx + 1))
done
