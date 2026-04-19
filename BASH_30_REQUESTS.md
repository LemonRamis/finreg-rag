# 30 Bash-запросов для FAST/RAG (готовый демо-набор)

## Быстрый старт

```bash
WEBHOOK="http://localhost:5678/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat"
```

Опционально: замени `WEBHOOK` на Cloudflare URL, если показываешь демо удалённо.

## 1) Короткие entity lookup (FAST)

```bash
# 01
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Дельта Плюс Павлодар","sessionId":"demo-01"}'
# 02
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Альянс Групп Алматы","sessionId":"demo-02"}'
# 03
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Гранит Трейд Астана","sessionId":"demo-03"}'
# 04
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Какой статус у компании АО \"Дельта Плюс\"?","sessionId":"demo-04"}'
# 05
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Когда зарегистрирована компания ИП \"Альянс Групп\"?","sessionId":"demo-05"}'
# 06
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Чем занимается компания АО \"Гранит Трейд\"?","sessionId":"demo-06"}'
```

## 2) Фильтры, list и count (FAST)

```bash
# 07
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Сколько активных компаний в Павлодаре?","sessionId":"demo-07"}'
# 08
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Найди активные компании в Алматы","sessionId":"demo-08"}'
# 09 (ожидается дизамбигуация)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Чем занимается компания Альянс?","sessionId":"demo-09"}'
# 10 (unsupported поле)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Какая выручка у АО \"Дельта Плюс\" за 2025 год?","sessionId":"demo-10"}'
# 11 (unsupported поле)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Кто владелец ИП \"Альянс Групп\"?","sessionId":"demo-11"}'
# 12
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Сколько ликвидированных компаний в Астане?","sessionId":"demo-12"}'
# 13
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Найди компании в Астане","sessionId":"demo-13"}'
# 14
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Покажи компании в Караганде","sessionId":"demo-14"}'
# 15
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/fast Какой статус у компании ИП \"ЭкоГрупп\"?","sessionId":"demo-15"}'
```

## 3) Семантические и гибридные сценарии (RAG)

```bash
# 16
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Дельта Плюс Павлодар","sessionId":"demo-16"}'
# 17
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Альянс Групп Алматы","sessionId":"demo-17"}'
# 18
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Чем занимается компания ИП \"Альянс Групп\"?","sessionId":"demo-18"}'
# 19
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Какой статус у компании АО \"Гранит Трейд\"?","sessionId":"demo-19"}'
# 20
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Сколько активных компаний в Павлодаре?","sessionId":"demo-20"}'
# 21
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Найди компании, похожие на IT-сферу в Алматы","sessionId":"demo-21"}'
# 22
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Что есть по теме обслуживания оборудования в Астане?","sessionId":"demo-22"}'
# 23
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Найди технологические компании в Павлодаре","sessionId":"demo-23"}'
# 24
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Покажи компании про логистику в Алматы","sessionId":"demo-24"}'
# 25 (ожидается дизамбигуация/нехватка контекста)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Чем занимается компания Альянс?","sessionId":"demo-25"}'
```

## 4) Unsupported и переключение режима

```bash
# 26 (unsupported поле)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Кто владелец АО \"Дельта Плюс\"?","sessionId":"demo-26"}'
# 27 (unsupported поле)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/rag Какая выручка у АО \"Дельта Плюс\" за 2025 год?","sessionId":"demo-27"}'
# 28 (альтернативный синтаксис mode)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/mode fast Дельта Плюс Павлодар","sessionId":"demo-28"}'
# 29 (альтернативный синтаксис mode)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"/mode rag Чем занимается компания ИП \"Альянс Групп\"?","sessionId":"demo-29"}'
# 30 (дефолтный режим без префикса)
curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" -d '{"action":"sendMessage","chatInput":"Гранит Трейд Астана","sessionId":"demo-30"}'
```

## Быстрый прогон всех 30

```bash
bash /Users/ramis/Работа/Проекты/ФИНРЕГ/scripts/run_30_requests.sh
```

Только первые N запросов:

```bash
MAX_REQUESTS=5 bash /Users/ramis/Работа/Проекты/ФИНРЕГ/scripts/run_30_requests.sh
```
