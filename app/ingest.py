import csv
from pathlib import Path

from app.config import settings
from app.embeddings import embed_text
from app.qdrant_store import recreate_collection, upsert_documents

CSV_FIELD_MAP = {
    "БИН": "bin",
    "Название": "name",
    "Город": "city",
    "Вид деятельности": "activity",
    "Статус": "status",
    "Дата регистрации": "registration_date",
}


def build_document(payload: dict[str, str]) -> str:
    return (
        f"BIN: {payload['bin']}\n"
        f"Name: {payload['name']}\n"
        f"City: {payload['city']}\n"
        f"Activity: {payload['activity']}\n"
        f"Status: {payload['status']}\n"
        f"Registration date: {payload['registration_date']}"
    )


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {
        target_key: (row.get(source_key) or "").strip()
        for source_key, target_key in CSV_FIELD_MAP.items()
    }


def run_ingest(csv_file_path: str | None = None) -> dict[str, int | str]:
    source_path = Path(csv_file_path or settings.csv_file_path)
    if not source_path.exists():
        raise FileNotFoundError(f"CSV file not found: {source_path}")

    documents: list[dict[str, object]] = []
    with source_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            payload = normalize_row(row)
            document = build_document(payload)
            payload["document"] = document
            documents.append(
                {
                    "embedding": embed_text(document),
                    "payload": payload,
                }
            )

    recreate_collection()
    upsert_documents(documents)
    return {
        "status": "ok",
        "collection": settings.qdrant_collection,
        "documents_indexed": len(documents),
        "source_file": str(source_path),
    }
