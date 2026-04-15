# Local RAG MVP — Инструкция Для Проверки

## Кратко

Ниже — готовый доступ для быстрой проверки MVP без локального развёртывания на вашей стороне.

Стенд для проверки полностью локальный: все сервисы (`n8n`, `Ollama`, `Qdrant`, `FastAPI`) запущены на `MacBook Air 15" (M4), 24 GB RAM / 512 GB SSD`, без использования внешних LLM/API.

## Публичная Точка Входа

`POST`:

`https://pour-magazine-qualified-gel.trycloudflare.com/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat`

## Доступ К Интерфейсу n8n (Для Просмотра Workflow)

Ссылка:

`https://pour-magazine-qualified-gel.trycloudflare.com/home/workflows`

Тестовые данные для авторизации:

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
curl -X POST "https://pour-magazine-qualified-gel.trycloudflare.com/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sendMessage",
    "chatInput": "Найди активные IT-компании в Алматы",
    "sessionId": "manager-test"
  }'
```

## Рекомендованные Тестовые Запросы

1. `Найди активные IT-компании в Алматы`
2. `Какой статус у компании ТОО "НурТех Групп"`
3. `Найди строительные компании в Астане`

## Что Ожидать В Ответе

- Ответ приходит в поле `response.text`.
- Возможна задержка ответа (локальная инференс-модель).

## Важно

Если ссылка перестанет открываться, будет отправлена новая: `trycloudflare` URL может меняться после перезапуска tunnel.
