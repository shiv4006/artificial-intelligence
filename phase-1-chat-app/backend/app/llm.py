from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

groq_client = AsyncOpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url, max_retries=0)
# Ollama ignores the API key, but the SDK requires one.
ollama_client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_base_url, max_retries=0)

def provider_for(model: str) -> str:
    return "ollama" if model in settings.ollama_models else "groq"

async def stream_chat(model: str, messages: list[dict]) -> AsyncIterator[tuple[str, Any]]:
    """Yield ("token", text) for each piece of the reply, then ("finish", reason) and ("usage", {...})."""
    extra = {}
    if model.startswith("openai/gpt-oss"):
        extra["reasoning_effort"] = "low"
    
    client = ollama_client if provider_for(model) == "ollama" else groq_client
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        **extra,
    )
    
    async for chunk in stream:
        if chunk.usage:
            details = chunk.usage.completion_tokens_details
            yield "usage", {
                "prompt_tokens": chunk.usage.prompt_tokens,
                "completion_tokens": chunk.usage.completion_tokens,
                "reasoning_tokens": details.reasoning_tokens if details else None,
            }
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        if choice.delta.content:
            yield "token", choice.delta.content
        if choice.finish_reason:
            yield "finish", choice.finish_reason