# Local RAG MVP для поиска по CSV базе юрлиц Казахстана

Простой полностью локальный MVP RAG-системы для поиска по базе юридических лиц Казахстана. Проект сделан в low-code формате через `n8n`: ingest и retrieval собраны визуальными workflow, без отдельного Python/FastAPI сервиса.

## Что внутри

- `n8n` оркестрирует загрузку CSV, подготовку документов и RAG-запрос.
- `Qdrant` хранит эмбеддинги и метаданные записей.
- `Ollama` запускает локальную LLM `gemma3:4b` и модель эмбеддингов `bge-m3`.
- `one-row-per-chunk`: каждая строка CSV превращается в один документ.
- Все компоненты запускаются локально через Docker Compose.
- Тестовый стенд: `MacBook Air 15" (M4), 24 GB RAM / 512 GB SSD`.

## Стек

- `n8n:2.2.6`
- `qdrant/qdrant:v1.16.2`
- `ollama/ollama:latest`
- `LLM`: `gemma3:4b`
- `Embeddings`: `bge-m3`

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

1. `When chat message received` принимает вопрос пользователя из n8n Chat.
2. `Ollama Embeddings` считает embedding вопроса.
3. `Qdrant Vector Store` ищет похожие документы в коллекции `kz_companies`.
4. `Vector Store Retriever` возвращает `topK = 3` документов.
5. `Question Answering Chain` передаёт найденный контекст в `gemma3:4b`.
6. Модель отвечает только по контексту.

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
docker exec rag-ollama ollama pull bge-m3
```

### 3. Настроить credentials в n8n

Открой `http://localhost:5678` и создай:

- `Ollama` credential с base URL `http://ollama:11434`
- `Qdrant` credential с base URL `http://qdrant:6333`

## Как выполнить ingest

1. Импортируй workflow [ingest_workflow.json](/Users/ramis/Работа/Проекты/ФИНРЕГ/n8n/ingest_workflow.json).
2. Убедись, что файл `data/sample_companies.csv` доступен в контейнере как `/home/node/.n8n-files/sample_companies.csv`.
3. При необходимости очисти старую коллекцию:

```bash
curl -X DELETE http://localhost:6333/collections/kz_companies
```

4. Запусти workflow вручную через `Execute workflow`.
5. После успешного выполнения данные будут загружены в коллекцию `kz_companies`.

## Как сделать запрос

Текущая версия query workflow использует `Chat Trigger` в публичном webhook-режиме.

1. Импортируй workflow [query_workflow.json](/Users/ramis/Работа/Проекты/ФИНРЕГ/n8n/query_workflow.json).
2. Открой workflow `Local RAG Query V2`.
3. Запусти или опубликуй workflow.
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
- `Найди строительные компании в Астане`

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

- Отдельная краткая инструкция: [MANAGER_DEMO_INSTRUCTIONS.md](/Users/ramis/Работа/Проекты/ФИНРЕГ/MANAGER_DEMO_INSTRUCTIONS.md)

## Итог

Проект демонстрирует полностью локальный RAG pipeline:

`CSV -> one-row-per-chunk -> embeddings -> Qdrant -> semantic retrieval -> answer by local Ollama LLM`

Этого достаточно для локального MVP, демонстрации логики RAG и дальнейшего расширения в полноценный backend при необходимости.
