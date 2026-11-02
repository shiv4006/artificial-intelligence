import tiktoken

from app import llm
from app.config import settings

# gpt-oss models use this tokenizer. Llama 3.1 has its own, so for Llama the count is an estimate.
encoding = tiktoken.get_encoding("o200k_harmony")

# Each message also costs a few tokens for its role and the separators around it.
TOKENS_PER_MESSAGE = 4

SUMMARY_PROMPT = """
You keep a running summary of a chat between a user and an assistant.
Update the summary with the new messages. Keep every fact the user gave about themselves (name, preferences, numbers, plans) and any decisions or open questions. Drop small talk.
Write at most 150 words. Reply with only summary.
"""

def count_tokens(messages: list[dict]) -> int:
    return sum(len(encoding.encode(m["content"])) + TOKENS_PER_MESSAGE for m in messages)

def first_messages(messages: list[dict], max_tokens: int) -> list[dict]:
    """The oldest messages that fit in max_tokens (always at least one)."""
    kept, total = [], 0
    for message in messages:
        total += count_tokens([message])
        if kept and total > max_tokens:
            break
        kept.append(message)
    
    return kept

def last_messages(messages: list[dict], max_tokens: int) -> list[dict]:
    """Strategy A, sliding window: the newest messages that fit in max_tokens (always at least one)."""
    return first_messages(messages[::-1], max_tokens)[::-1]

async def summarize(summary: str | None, messages: list[dict]) -> str:
    """Strategy B: fold the messages into the running summary with one call to the cheap model."""
    transcript = "\n\n".join(f"{m['role']}: {m['content']}" for m in messages)
    return await llm.complete(settings.utility_model, [
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": f"Summary so far:\n{summary or '(empty)'}\n\nNew messages: \n{transcript}"},
    ])
    
async def build_messages(conversation: dict, history: list[dict]) -> tuple[list[dict], tuple[str, int] | None]:
    """The messages to send for this turn, system prompt first.
    
    Also returns (summary, summarized_through) when old messages were folded into the summary,
    so the caller can save it. Otherwise None.
    """
    budget = settings.context_max_tokens
    system = conversation["system_prompt"]
    update = None
    
    if settings.context_strategy == "none":
        recent = history
    elif settings.context_strategy == "window":
        recent = last_messages(history, budget)
    else:
        summary = conversation["summary"]
        through = conversation["summarized_through"] or 0
        recent = [m for m in history if m["id"] > through]
        # Over budget: fold the oldest messages into the summary, half a budget at a time,
        # until the summary plus the messages after it fit. The newest message is never folded.
        while len(recent) > 1 and len(encoding.encode(summary or "")) + count_tokens(recent) > budget:
            old = first_messages(recent[:-1], budget // 2)
            summary = await summarize(summary, old)
            recent = recent[len(old):]
            update = (summary, old[-1]["id"])
        if summary:
            system += f"\n\nSummary of the earlier conversation:\n{summary}"
        
    messages = [{"role": "system", "content": system}]
    messages += [{"role": m["role"], "content": m["content"]} for m in recent]
    return messages, update