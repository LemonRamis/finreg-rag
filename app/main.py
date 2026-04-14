from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.embeddings import embed_text
from app.ingest import run_ingest
from app.llm import generate_answer
from app.qdrant_store import get_qdrant_client, search_documents


class IngestRequest(BaseModel):
    csv_file_path: str | None = Field(
        default=None,
        description="Optional path to CSV file. Defaults to configured sample file.",
    )


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)


def check_dependencies() -> None:
    get_qdrant_client().get_collections()
    response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=10)
    response.raise_for_status()


@asynccontextmanager
async def lifespan(_: FastAPI):
    check_dependencies()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
def ingest(request: IngestRequest) -> dict[str, int | str]:
    try:
        return run_ingest(request.csv_file_path)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {error}") from error


@app.post("/query")
def query(request: QueryRequest) -> dict[str, object]:
    try:
        query_embedding = embed_text(request.question)
        matches = search_documents(
            query_embedding=query_embedding,
            limit=request.top_k or settings.top_k,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {error}") from error

    if not matches:
        return {
            "answer": "Недостаточно данных в базе, чтобы ответить на вопрос.",
            "matches": [],
        }

    context = "\n\n".join(
        f"Document {index}:\n{match['payload']['document']}"
        for index, match in enumerate(matches, start=1)
    )

    try:
        answer = generate_answer(request.question, context)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {error}") from error

    return {
        "answer": answer,
        "matches": matches,
    }
