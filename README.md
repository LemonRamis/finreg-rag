# Локальный MVP RAG для поиска по CSV базе юрлиц Казахстана (Low-Code)

Простой полностью локальный RAG-пайплайн, реализованный **исключительно визуальными средствами (n8n Advanced AI)** без использования самописного Python-бэкенда.

- `n8n` выступает полноценным оркестратором: загружает CSV, чанкует, встраивает (embeds) и извлекает данные (retrieves).
- `Qdrant` хранит векторные эмбеддинги и метаданные.
- `Ollama` запускает локальную LLM `qwen3.5:4b` и модель эмбеддингов `bge-m3`.

## Архитектура

### Ingest (n8n Workflow)
1. Нода `Read CSV` читает локальный файл из `data/`.
2. Нода `Spreadsheet File` сериализует CSV в построчные JSON-объекты.
3. Нода `Code` формирует единый текст `pageContent` на одну компанию и подготавливает поля метаданных.
4. Нода `Default Data Loader` в режиме `Load All Input Data` с JSON pointer `/pageContent` превращает запись в один LangChain-документ и прикладывает метаданные.
5. Нода `Qdrant Vector Store` через "кубик" `Ollama Embeddings` высчитывает вектор документа и делает Upsert в коллекцию.

### Retrieval (n8n Workflow)
1. Webhook `POST /rag-query` принимает вопрос в JSON-поле `chatInput`.
2. Нода `Qdrant Vector Store` открывает коллекцию `kz_companies`.
3. Нода `Vector Store Retriever` запрашивает `Top-K = 3` ближайших документов.
4. Нода `Question Answering Chain` (LangChain) связывает модель `Ollama (qwen)` и ретривер, добавляет найденный контекст в промпт и генерирует ответ.

## Структура проекта

```text
.
├── data
│   └── sample_companies.csv
├── n8n
│   ├── ingest_workflow.json
│   ├── query_workflow.json
│   ├── ingest_workflow_v2.json
│   └── query_workflow_v2.json
├── docker-compose.yml
├── README.md
└── Task
```

## Как запустить

### 1. Поднять сервисы (n8n, Qdrant, Ollama)

```bash
docker compose -p finreg up -d
```

### 2. Скачать локальные модели в Ollama

Для генерации ответов (LLM):
```bash
docker exec rag-ollama ollama pull qwen3.5:4b
```

Для эмбеддингов:
```bash
docker exec rag-ollama ollama pull bge-m3
```

### 3. Настройка n8n

1. Откройте `http://localhost:5678` в браузере.
2. Пройдите быструю настройку (если запускаете впервые).
3. Создайте новые Credentials для:
   - **Ollama**: `http://ollama:11434`
   - **Qdrant**: `http://qdrant:6333`
4. Импортируйте сначала `n8n/ingest_workflow_v2.json`.
5. Перед повторной загрузкой удалите старую коллекцию, если она уже была заполнена неверно:

```bash
curl -X DELETE http://localhost:6333/collections/kz_companies
```

6. Запустите ingest workflow через `Execute workflow`, чтобы заново загрузить CSV в векторную БД.
7. Импортируйте `n8n/query_workflow_v2.json` и опубликуйте workflow, чтобы production webhook начал принимать запросы.

## Как сделать запрос

Через API webhook, который прослушивает n8n:

```bash
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"chatInput":"Найди активные IT-компании в Алматы"}'
```

Ожидаемый формат ответа:

```json
{
  "response": "..."
}
```

## Важно (ограничения MVP)

- Для стабильной локальной работы в текущем окружении используется `qwen3.5:4b` вместо `qwen3.5:9b` (ограничение RAM/CPU при inference).
- Решение сделано в формате Low-Code через `n8n` (без отдельного FastAPI-сервиса), при этом весь RAG pipeline полностью локальный: CSV ingest -> embeddings -> Qdrant -> retrieval -> Ollama.
