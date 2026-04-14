from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Local RAG MVP"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "kz_companies"
    qdrant_distance: str = "Cosine"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:9b"
    ollama_temperature: float = 0.2

    embedding_model_name: str = "BAAI/bge-m3"
    csv_file_path: str = "data/sample_companies.csv"
    top_k: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
