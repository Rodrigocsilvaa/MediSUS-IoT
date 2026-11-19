"""Generate a Portuguese summary of recent readings using the OpenAI API."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from medisus_iot.storage import ReadingStore


API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-mini"
SYSTEM_PROMPT = (
    "Você resume leituras sintéticas de temperatura para uma demonstração acadêmica. "
    "Escreva em português, de forma curta e clara. Descreva os valores e os alertas "
    "já marcados pelo sistema. O campo alert foi calculado por regras fixas de "
    "demonstração: não reavalie nem invente limites. Não recomende ações clínicas, "
    "não diga que um medicamento está seguro ou inseguro e informe que o resumo não "
    "substitui avaliação profissional."
)


def generate_summary(
    readings: list[dict[str, str | float | bool]],
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> str:
    if not api_key.strip():
        raise ValueError("OPENAI_API_KEY must be configured")
    if not readings:
        raise ValueError("there are no readings to summarize")
    if not model.strip():
        raise ValueError("OPENAI_MODEL cannot be empty")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({"readings": readings}, ensure_ascii=False),
            },
        ],
        "temperature": 0.2,
        "max_completion_tokens": 250,
    }
    request = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"AI API request failed with HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"AI API request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError("AI API request timed out") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("AI API returned invalid JSON") from exc

    try:
        summary = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("AI API response did not contain a summary") from exc
    if not isinstance(summary, str) or not summary.strip():
        raise RuntimeError("AI API response contained an empty summary")
    return summary.strip()


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key.strip():
        raise SystemExit("Defina OPENAI_API_KEY para gerar o resumo com IA.")

    store = ReadingStore(os.getenv("DATABASE_PATH", "readings.sqlite3"))
    try:
        readings = store.latest_readings(limit=20)
    finally:
        store.close()
    if not readings:
        raise SystemExit("Nenhuma leitura encontrada. Execute o simulador primeiro.")

    try:
        summary = generate_summary(
            readings,
            api_key,
            os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        )
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(str(exc)) from exc
    print("Resumo gerado por IA (apoio informativo; não é avaliação clínica):")
    print(summary)


if __name__ == "__main__":
    main()
