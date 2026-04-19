# Local RAG MVP для поиска по CSV базе юрлиц Казахстана

Простой полностью локальный MVP RAG-системы для поиска по базе юридических лиц Казахстана. Проект сделан в low-code формате через `n8n`: ingest и retrieval собраны визуальными workflow, без отдельного Python/FastAPI сервиса.

## Что внутри

- `n8n` оркестрирует загрузку CSV, подготовку документов и RAG-запрос.
- `Qdrant` хранит эмбеддинги и метаданные записей.
- `Ollama` запускает локальную LLM `gemma3:4b` и модель эмбеддингов `bge-m3:latest`.
- `one-row-per-chunk`: каждая строка CSV превращается в один документ.
- Финальный ответ формируется детерминированно из `metadata` Qdrant (без генерации фактов LLM).
- Все компоненты запускаются локально через Docker Compose.
- Тестовый стенд: `MacBook Air 15" (M4), 24 GB RAM / 512 GB SSD`.

## Стек

- `n8n:2.2.6`
- `qdrant/qdrant:v1.16.2`
- `ollama/ollama:latest`
- `LLM`: `gemma3:4b`
- `Embeddings`: `bge-m3:latest`

## Статус Проекта (Проверено 2026-04-18)

Проверена целостность, работоспособность и anti-hallucination логика:

- `docker compose -p finreg config` проходит без ошибок.
- `docker compose -p finreg ps`: контейнеры `rag-n8n`, `rag-qdrant`, `rag-ollama` в статусе `Up`.
- В Qdrant есть коллекция `kz_companies`; количество точек: `200`.
- В `data/sample_companies.csv` количество строк (без заголовка): `200`.
- End-to-end запросы через webhook (`curl`) стабильно возвращают `HTTP 200`.
- Исправлен критичный кейс: запросы про `активные` компании больше не возвращают записи со статусом `Ликвидировано`.
- Добавлен hard-guard для unsupported запросов (`выручка`, `крупнейшие`, `топ N` и др.): ответ строго `Недостаточно данных в контексте...`.
- Добавлена явная дизамбигуация: при нескольких совпадениях по имени система запрашивает уточнение (`город` или `юрформа`), вместо «угадывания».
- Для exact/filter/count сценариев используется metadata-only путь без обязательного vector retrieval в hot path.

## Архитектура

### Ingest

1. `Read CSV` читает файл `data/sample_companies.csv`.
2. `Spreadsheet File` разбирает CSV в JSON-строки.
3. `Format Payload` собирает документ вида:

```text
БИН: ...
Название: ...
Город: ...
Вид деятельности: ...
Статус: ...
Дата регистрации: ...
```

4. `Default Data Loader` превращает запись в LangChain-документ.
5. `Qdrant Vector Store` + `Ollama Embeddings` считают embedding и загружают документ в коллекцию `kz_companies`.

### Retrieval

1. `When chat message received` принимает вопрос пользователя.
2. `Prepare Query Strategy` определяет `queryMode` (`count`, `bin_lookup`, `status_lookup`, `registration_date_lookup`, `activity_lookup`, `list`, `generic`, `unsupported`), строит metadata-фильтры (`bin/name/city/status/activity`), выделяет `companyHint` и `legalForm`, выбирает `retrievalMode` (`none/metadata/semantic`) и `answerBranch` (`fast`/`rag`).
3. `Route Answer Branch` переключает маршрут:
   - `fast` -> `Retrieve Candidates` -> `Format Final Answer`
   - `rag` -> `Question Answering Chain` (через `Vector Store Retriever` + `Qdrant Vector Store` + `Ollama Embeddings`) -> `Format Final Answer`
4. `Retrieve Candidates` (для `fast`):
   - `none`: short-circuit для `unsupported`/`cacheHit`;
   - `metadata`: Qdrant `count + scroll` по фильтрам;
   - `semantic`: Ollama embeddings + Qdrant vector search (fallback для размытых запросов).
5. `Format Final Answer`:
   - в `fast` режиме детерминированно собирает ответ из `document.metadata`, добавляет `Подтверждение`, пишет/читает cache;
   - в `rag` режиме возвращает итог `Question Answering Chain` (с пост-обработкой JSON-ответа цепочки).
6. Если найдено несколько кандидатов для lookup-запроса (fast), включается явная дизамбигуация: запрос уточнения (`город`/`юрформа`) + список вариантов (название, город, БИН).
7. Для unsupported или пустого результата возвращается строгий safe-fallback: `Недостаточно данных в контексте.`

Важно: нормализация ответа и fallback реализованы только внутри workflow (узел `Format Final Answer`), клиентские скрипты пост-обработки не используются.

### Анти-галлюцинации (Критично)

- Источник фактов: только `Qdrant metadata` (`bin`, `name`, `city`, `status`, `activity`, `registration_date`).
- Если поле не поддерживается источником данных, pipeline не пытается «додумать» ответ.
- Если фильтры дали пустой набор, возвращается только `Недостаточно данных в контексте.`.
- Если найдено несколько совпадений по имени, pipeline не выбирает запись произвольно, а просит уточнить `город` или `юрформу`.
- После изменений workflow в `n8n:2.2.6` обязательно активируй новую `versionId` (через UI или `/rest/workflows/:id/activate`), иначе webhook может остаться на старой версии.

Параметры производительности в текущей версии:

- `numCtx: 2048`
- `numPredict: 96`
- `temperature: 0`

## Структура проекта

```text
.
├── data
│   └── sample_companies.csv
├── n8n
│   ├── ingest_workflow.json
│   └── query_workflow.json
├── MANAGER_DEMO_INSTRUCTIONS.md
├── docker-compose.yml
├── README.md
└── Task
```

## Быстрый старт

### 1. Поднять сервисы

```bash
docker compose -p finreg up -d
```

Сервисы будут доступны по адресам:

- `n8n`: `http://localhost:5678`
- `Qdrant`: `http://localhost:6333`
- `Ollama`: `http://localhost:11434`

### 2. Скачать модели в Ollama

```bash
docker exec rag-ollama ollama pull gemma3:4b
docker exec rag-ollama ollama pull bge-m3:latest
```

### 3. Настроить credentials в n8n

Открой `http://localhost:5678` и создай:

- `Ollama` credential с base URL `http://ollama:11434`
- `Qdrant` credential с base URL `http://qdrant:6333`

## Как выполнить ingest

1. Импортируй workflow `n8n/ingest_workflow.json`.
2. Убедись, что файл `data/sample_companies.csv` доступен в контейнере как `/home/node/.n8n-files/sample_companies.csv`.
3. При необходимости очисти старую коллекцию:

```bash
curl -X DELETE http://localhost:6333/collections/kz_companies
```

4. Запусти workflow вручную через `Execute workflow`.
5. После успешного выполнения данные будут загружены в коллекцию `kz_companies`.

## Как сделать запрос

Текущая версия query workflow использует `Chat Trigger` в публичном webhook-режиме.

1. Импортируй workflow `n8n/query_workflow.json`.
2. Открой workflow `Local RAG Query V2`.
3. После любых изменений workflow активируй новую версию:

```bash
curl -sS -X POST "http://localhost:5678/rest/workflows/nQjnLUKAEuy82DSP/activate" \
  -H "Content-Type: application/json" \
  -d '{"versionId":"<NEW_VERSION_ID>"}'
```

4. Отправь вопрос через встроенную панель чата в n8n или через webhook:

```bash
curl -X POST "http://localhost:5678/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sendMessage",
    "chatInput": "Найди активные IT-компании в Алматы",
    "sessionId": "local-test"
  }'
```

Примеры запросов:

- `Найди активные IT-компании в Алматы`
- `Какой статус у компании НурТех Групп`
- `Какой статус у нуртех групп?` (ожидаемый clarify при нескольких совпадениях)
- `Какой статус у АО нуртех групп?` (ожидаемый однозначный ответ)
- `Найди строительные компании в Астане`
- `Сколько ликвидированных компаний в Павлодаре?`
- `Какая выручка у ТОО "НурТех Групп" за 2025 год?` (ожидаемый safe-fallback)

Переключение ветки формирования ответа (feature):

- По умолчанию используется `FAST` ветка.
- Явно `FAST`: добавить префикс `/fast` или `/mode fast`.
- Явно `RAG`: добавить префикс `/rag` или `/mode rag`.
- Для наглядности в начале ответа выводится метка режима: `[MODE: FAST]` или `[MODE: RAG]`.

Примеры:

- `/fast Какой статус у компании ТОО "НурТех Групп"?`
- `/rag Какой статус у компании ТОО "НурТех Групп"?`

## Быстрые Проверки После Запуска

```bash
docker compose -p finreg ps
curl -sS http://localhost:5678/healthz
curl -sS http://localhost:6333/collections | jq
curl -sS http://localhost:11434/api/tags | jq
```

Проверка, что ingest действительно загружен:

```bash
curl -sS -X POST http://localhost:6333/collections/kz_companies/points/count \
  -H "Content-Type: application/json" \
  -d '{"exact": true}'
```

## Что хранится в Qdrant

Для каждой записи сохраняются:

- `pageContent`
- `bin`
- `name`
- `city`
- `activity`
- `status`
- `registration_date`

Коллекция: `kz_companies`

## Ограничения MVP

- Проект реализован в low-code формате через `n8n`, без отдельного backend-сервиса.
- Для стабильной локальной работы используется `gemma3:4b`: модель компактная и подходит для локального CPU/RAM-профиля.
- На CPU inference может быть медленным, особенно на длинном контексте.
- Workflow ориентирован на локальную демонстрацию и smoke test, а не на production-нагрузку.

## Демо Для Менеджера

- Отдельная краткая инструкция: `MANAGER_DEMO_INSTRUCTIONS.md`
- Отчет с 5 репрезентативными прогонами: `отчет.md`

## Проверка Из Терминала (Только Workflow)

Запросы выполняются напрямую в webhook workflow без промежуточных скриптов:

```bash
curl -sS -X POST "http://localhost:5678/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sendMessage",
    "chatInput": "Найди активные IT-компании в Алматы",
    "sessionId": "local-test"
  }'
```

Только текст ответа:

```bash
curl -sS -X POST "http://localhost:5678/webhook/62eb0006-34f6-4d09-987e-edf71ca0b255/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sendMessage",
    "chatInput": "Какой статус у компании ТОО \"НурТех Групп\"?",
    "sessionId": "local-test"
  }' | jq -r '.response.text'
```

Рекомендация: запускать запросы последовательно (не параллельно), так как локальная LLM на CPU может заметно замедляться при конкурентных вызовах.

## Итог

Проект демонстрирует полностью локальный RAG pipeline:

`CSV -> one-row-per-chunk -> embeddings -> Qdrant -> filtered retrieval -> deterministic answer formatter`

Этого достаточно для локального MVP, демонстрации логики RAG и дальнейшего расширения в полноценный backend при необходимости.
