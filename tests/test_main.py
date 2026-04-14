from fastapi.testclient import TestClient

from app import main


def test_healthcheck_returns_ok() -> None:
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_endpoint_uses_default_path_when_body_empty(monkeypatch) -> None:
    client = TestClient(main.app)
    captured: dict[str, str | None] = {}

    def fake_run_ingest(csv_file_path: str | None) -> dict[str, object]:
        captured["csv_file_path"] = csv_file_path
        return {"status": "ok", "source_file": "data/sample_companies.csv"}

    monkeypatch.setattr(main, "run_ingest", fake_run_ingest)

    response = client.post("/ingest", json={})

    assert response.status_code == 200
    assert captured["csv_file_path"] is None
    assert response.json() == {"status": "ok", "source_file": "data/sample_companies.csv"}


def test_ingest_endpoint_returns_404_for_missing_file(monkeypatch) -> None:
    client = TestClient(main.app)

    def fake_run_ingest(_: str | None) -> dict[str, object]:
        raise FileNotFoundError("CSV file not found")

    monkeypatch.setattr(main, "run_ingest", fake_run_ingest)

    response = client.post("/ingest", json={"csv_file_path": "missing.csv"})

    assert response.status_code == 404
    assert response.json()["detail"] == "CSV file not found"


def test_query_returns_matches_and_answer(monkeypatch) -> None:
    client = TestClient(main.app)

    monkeypatch.setattr(main, "embed_text", lambda question: [0.1, 0.2])
    monkeypatch.setattr(
        main,
        "search_documents",
        lambda query_embedding, limit: [
            {
                "score": 0.99,
                "payload": {
                    "document": "BIN: 123\nName: ТОО Тест",
                    "name": "ТОО Тест",
                },
            }
        ],
    )
    monkeypatch.setattr(main, "generate_answer", lambda question, context: "Найдена компания ТОО Тест.")

    response = client.post("/query", json={"question": "Найди ТОО Тест", "top_k": 3})

    assert response.status_code == 200
    assert response.json()["answer"] == "Найдена компания ТОО Тест."
    assert len(response.json()["matches"]) == 1


def test_query_returns_fallback_when_no_matches(monkeypatch) -> None:
    client = TestClient(main.app)

    monkeypatch.setattr(main, "embed_text", lambda question: [0.1, 0.2])
    monkeypatch.setattr(main, "search_documents", lambda query_embedding, limit: [])

    response = client.post("/query", json={"question": "Найди несуществующую компанию"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Недостаточно данных в базе, чтобы ответить на вопрос.",
        "matches": [],
    }


def test_query_validates_short_question() -> None:
    client = TestClient(main.app)

    response = client.post("/query", json={"question": "ok"})

    assert response.status_code == 422
