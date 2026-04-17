# Local RAG MVP — Инструкция Для Проверки (Manager Demo)

## Кратко

Ниже — готовый доступ для быстрой проверки MVP без локального развёртывания на вашей стороне.

Стенд полностью локальный: сервисы (`n8n`, `Ollama`, `Qdrant`) запущены на `MacBook Air 15" (M4), 24 GB RAM / 512 GB SSD`, без внешних LLM/API.

## Актуальные Ссылки Для Демо

Ссылки берутся из вывода `./run_demo_tunnel.sh` и действуют, пока запущен туннель.

- `n8n UI`: `https://<your-current-subdomain>.trycloudflare.com/home/workflows`
- `Chat webhook (POST)`: `https://<your-current-subdomain>.trycloudflare.com/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat`

Пример активной ссылки на момент последнего запуска:

- `n8n UI`: `https://holdings-quit-exercise-witnesses.trycloudflare.com/home/workflows`
- `Chat webhook`: `https://holdings-quit-exercise-witnesses.trycloudflare.com/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat`

## Доступ К Интерфейсу n8n (Для Просмотра Workflow)

- Логин: `nazarov.ramis66@gmail.com`
- Пароль: `ZLge69zST8RE@ua`

## Формат Запроса

```json
{
  "action": "sendMessage",
  "chatInput": "Найди активные IT-компании в Алматы",
  "sessionId": "manager-test"
}
```

## Быстрый Тест Через cURL

```bash
curl -sS -X POST "https://<your-current-subdomain>.trycloudflare.com/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sendMessage",
    "chatInput": "Какой статус у компании ТОО \"НурТех Групп\"?",
    "sessionId": "manager-test"
  }'
```

## Рекомендованные Тестовые Запросы

1. `Какой статус у компании ТОО "НурТех Групп"?`
2. `Сколько ликвидированных компаний в Павлодаре?`
3. `Какая выручка у ТОО "НурТех Групп" за 2025 год?` (ожидаемый safe-fallback)

## Что Ожидать В Ответе

- Ответ приходит в поле `response.text`.
- По factual-запросам приходит `Подтверждение` из базы.
- Для неподдерживаемых полей (например `выручка`) возвращается `Недостаточно данных в контексте...`.

## Как Обновить Ссылку За 1 Минуту

1. Запустить скрипт:

```bash
cd /Users/ramis/Работа/Проекты/ФИНРЕГ
./run_demo_tunnel.sh
```

2. Скопировать из вывода:
- `n8n UI`
- `Chat webhook`

3. Отправить менеджеру.

## Готовый Текст Для Отправки Менеджеру

```text
Ильяс, добрый день! Ниже рабочая ссылка, открывается без Docker и без настройки с вашей стороны.

UI (просмотр): https://<your-current-subdomain>.trycloudflare.com/home/workflows
API (чат): https://<your-current-subdomain>.trycloudflare.com/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat

Пример теста:
Какой статус у компании ТОО "НурТех Групп"?

Если ссылка перестанет открываться, сразу пришлю новую (это временный demo tunnel).
```

## Важно

- `trycloudflare` URL временный и меняется после перезапуска tunnel.
- Ссылка работает, пока запущен `./run_demo_tunnel.sh`.
