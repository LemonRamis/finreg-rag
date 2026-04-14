from pathlib import Path

from app import ingest


def test_normalize_row_maps_and_strips_fields() -> None:
    row = {
        "БИН": " 123456789012 ",
        "Название": " ТОО Тест ",
        "Город": " Алматы ",
        "Вид деятельности": " IT ",
        "Статус": " Активно ",
        "Дата регистрации": " 2024-01-01 ",
    }

    assert ingest.normalize_row(row) == {
        "bin": "123456789012",
        "name": "ТОО Тест",
        "city": "Алматы",
        "activity": "IT",
        "status": "Активно",
        "registration_date": "2024-01-01",
    }


def test_build_document_formats_payload() -> None:
    payload = {
        "bin": "123456789012",
        "name": "ТОО Тест",
        "city": "Алматы",
        "activity": "IT",
        "status": "Активно",
        "registration_date": "2024-01-01",
    }

    assert ingest.build_document(payload) == (
        "BIN: 123456789012\n"
        "Name: ТОО Тест\n"
        "City: Алматы\n"
        "Activity: IT\n"
        "Status: Активно\n"
        "Registration date: 2024-01-01"
    )


def test_run_ingest_reads_csv_and_upserts_documents(monkeypatch, tmp_path: Path) -> None:
    csv_file = tmp_path / "companies.csv"
    csv_file.write_text(
        (
            "БИН,Название,Город,Вид деятельности,Статус,Дата регистрации\n"
            "123,ТОО Тест,Алматы,IT,Активно,2024-01-01\n"
            "456,ТОО Второе,Астана,Строительство,Неактивно,2023-05-10\n"
        ),
        encoding="utf-8",
    )

    recreate_calls: list[str] = []
    upserted_documents: list[dict[str, object]] = []

    monkeypatch.setattr(ingest, "embed_text", lambda text: [float(len(text))])
    monkeypatch.setattr(ingest, "recreate_collection", lambda: recreate_calls.append("called"))
    monkeypatch.setattr(
        ingest,
        "upsert_documents",
        lambda documents: upserted_documents.extend(documents),
    )

    result = ingest.run_ingest(str(csv_file))

    assert result["status"] == "ok"
    assert result["documents_indexed"] == 2
    assert result["source_file"] == str(csv_file)
    assert recreate_calls == ["called"]
    assert len(upserted_documents) == 2
    assert upserted_documents[0]["payload"]["document"].startswith("BIN: 123")
    assert upserted_documents[1]["payload"]["name"] == "ТОО Второе"


def test_run_ingest_raises_for_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.csv"

    try:
        ingest.run_ingest(str(missing_file))
    except FileNotFoundError as error:
        assert str(missing_file) in str(error)
    else:
        raise AssertionError("Expected FileNotFoundError for absent CSV file")
