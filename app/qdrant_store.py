from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import settings
from app.embeddings import get_embedding_dimension


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def recreate_collection() -> None:
    client = get_qdrant_client()
    client.recreate_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=models.VectorParams(
            size=get_embedding_dimension(),
            distance=models.Distance.COSINE,
        ),
    )


def upsert_documents(documents: list[dict[str, Any]]) -> None:
    client = get_qdrant_client()
    points = [
        models.PointStruct(
            id=index,
            vector=document["embedding"],
            payload=document["payload"],
        )
        for index, document in enumerate(documents, start=1)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)


def search_documents(query_embedding: list[float], limit: int) -> list[dict[str, Any]]:
    client = get_qdrant_client()
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_embedding,
        limit=limit,
        with_payload=True,
    )
    return [
        {
            "score": result.score,
            "payload": result.payload,
        }
        for result in results
    ]
