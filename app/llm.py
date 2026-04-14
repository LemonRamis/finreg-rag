import requests

from app.config import settings

SYSTEM_PROMPT = (
    "Ты работаешь только на основе переданного контекста.\n"
    "Ответь кратко и по делу.\n"
    "Если данных недостаточно — скажи об этом.\n"
    "Не придумывай информацию."
)


def generate_answer(question: str, context: str) -> str:
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Контекст:\n{context}\n\n"
        f"Вопрос: {question}\n"
        "Ответ:"
    )
    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.ollama_temperature,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()
