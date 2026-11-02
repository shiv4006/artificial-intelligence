from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

groq_client = AsyncOpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url, max_retries=0)
# Ollama ignores the API key, but the SDK requires one.
ollama_client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_base_url, max_retries=0)

# The task goes into the user message with the chat's first message marked as data. As a system prompt,
# the model answered or echoed the message instead of titling it.
TITLE_PROMPT = """
Write a title of 2 to 6 words for a chat that starts with the message below. Reply with only the title.

Message:
{message}
"""

def provider_for(model: str) -> str:
    return "ollama" if model in settings.ollama_models else "groq"

def client_for(model: str) -> AsyncOpenAI:
    return ollama_client if provider_for(model) == "ollama" else groq_client

def extra_params(model: str) -> dict:
    return {"reasoning_effort": "low"} if model.startswith("openai/gpt-oss") else {}

async def stream_chat(model: str, messages: list[dict]) -> AsyncIterator[tuple[str, Any]]:
    """Yield ("token", text) for each piece of the reply, then ("finish", reason) and ("usage", {...})."""
    stream = await client_for(model).chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        **extra_params(model),
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
            
async def complete(model: str, messages: list[dict]) -> str:
    """One call without streaming, for small jobs like summaries and titles."""
    response = await client_for(model).chat.completions.create(model=model, messages=messages, **extra_params(model))
    return (response.choices[0].message.content or "").strip()

async def make_title(first_message: str) -> str:
    title = await complete(settings.utility_model, [{"role": "user", "content": TITLE_PROMPT.format(message=first_message)}])
    return title.strip("\"'*# ").rstrip(".")[:60]