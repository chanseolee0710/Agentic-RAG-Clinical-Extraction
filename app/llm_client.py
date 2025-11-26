# app/llm_client.py

from typing import Any
from openai import OpenAI
from .config import settings

# Create OpenAI client using the API key from .env
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)


def summarize_note(note: str) -> tuple[str, Any]:
    """
    Summarize a medical note using OpenAI.

    The latest OpenAI SDK uses:
    client.chat.completions.create()
    """

    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please add it to your .env file."
        )

    system_prompt = (
        "You are a clinical documentation assistant. "
        "Summarize the following medical note into 3–5 concise bullet points, "
        "focusing on chief complaint, key history, exam findings, and plan."
        "Use the uploaded guidelines to further inform your summary, plan, and"
        "recommendations."
    )

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Medical note:\n{note}"},
        ],
        temperature=0.2,
    )

    summary_text = response.choices[0].message.content.strip()
    usage = response.usage
    return summary_text, usage
