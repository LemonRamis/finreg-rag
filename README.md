# Локальный MVP RAG для поиска по CSV базе юрлиц Казахстана

Простой полностью локальный RAG-пайплайн:

- `FastAPI` отвечает за ingest и retrieval.
- `Qdrant` хранит embeddings и metadata.
- `Ollama` запускает локальную LLM `qwen3.5:4b`.
- `BAAI/bge-m3` используется для embeddings.
- `n8n` оркестрирует два workflow: ingest и query.

## Архитектура

### Ingest

1. CSV читается построчно.
2. Каждая строка превращается в один документ.
3. Для документа считается embedding через `BAAI/bge-m3`.
4. В `Qdrant` создается коллекция `kz_companies`.
5. В коллекцию загружаются:
   - vector
   - payload: `bin`, `name`, `city`, `activity`, `status`, `registration_date`, `document`

### Retrieval

1. `/query` принимает вопрос.
2. Для вопроса считается embedding.
3. Выполняется `top-k` semantic search в `Qdrant`.
4. Из найденных документов собирается контекст.
5. Контекст отправляется в `Ollama` с моделью `qwen3.5:4b`.
6. LLM отвечает только на основе найденного контекста.

Промпт для LLM:

```text
Ты работаешь только на основе переданного контекста.
Ответь кратко и по делу.
Если данных недостаточно — скажи об этом.
Не придумывай информацию.
```

## Структура проекта

```text
.
├── app
│   ├── config.py
│   ├── embeddings.py
│   ├── ingest.py
│   ├── llm.py
│   ├── main.py
│   └── qdrant_store.py
├── data
│   └── sample_companies.csv
├── n8n
│   ├── ingest_workflow.json
│   └── query_workflow.json
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Как запустить

### 1. Поднять сервисы

```bash
docker compose -p finreg up -d --build
```

### 2. Скачать локальную LLM в Ollama

```bash
docker exec rag-ollama ollama pull qwen3.5:4b
```

### 3. Проверить, что API поднялся

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

## Как выполнить ingest

Через API:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"csv_file_path":"data/sample_companies.csv"}'
```

Через n8n:

1. Открыть `http://localhost:5678`
2. Импортировать `n8n/ingest_workflow.json`
3. Запустить workflow вручную через `Manual Trigger`

## Как сделать запрос

Через API:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Найди активные IT-компании в Алматы","top_k":5}'
```

Через n8n:

1. Импортировать `n8n/query_workflow.json`
2. Активировать workflow
3. Отправить POST-запрос на webhook:

```bash
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"question":"Найди строительные компании в Астане"}'
```

## Проверка на 3 запросах

После ingest можно проверить систему на таких вопросах:

1. `Найди активные IT-компании в Алматы`
2. `Какой статус у компании ТОО "НурТех Трейд"`
3. `Найди строительные компании в Астане`

Примечание: в приложенном `sample_companies.csv` нет явной активной IT-компании из Алматы, поэтому для первого запроса корректным поведением будет либо показать ближайшие семантически подходящие записи, либо честно ответить, что точных данных в контексте недостаточно.

Примеры запросов:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Найди активные IT-компании в Алматы"}'

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Какой статус у компании ТОО \"НурТех Трейд\""}'

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Найди строительные компании в Астане"}'
```

## Актуальный статус

- Стек протестирован локально в составе `rag-app`, `rag-qdrant`, `rag-ollama`, `rag-n8n`.
- `GET /health` отвечает `200 OK`.
- `POST /ingest` успешно индексирует `200` записей из `data/sample_companies.csv`.
- `POST /query` успешно возвращает ответ. Для вопроса `Какой статус у компании ТОО "НурТех Трейд"` система отвечает: `Активно.`

Важно:

- После долгой работы Docker Desktop на macOS `Ollama` может временно не загружать модель из-за состояния памяти Docker VM.
- Если `POST /query` падает по памяти или модель не стартует, самый надёжный способ восстановления — перезапустить Docker Desktop и снова поднять стек.

## Замечания

- Chunking намеренно максимально простой: `1 CSV row = 1 document`.
- Payload хранится отдельно в `Qdrant`, чтобы было удобно показывать найденные поля.
- Первая загрузка `BAAI/bge-m3` может занять время, потому что модель будет скачана локально в cache контейнера `app`.
- Первая загрузка `qwen3.5:4b` в `Ollama` тоже может занять несколько минут.
- Решение не использует внешние inference API: retrieval и generation выполняются локально через `Qdrant` и `Ollama`.
