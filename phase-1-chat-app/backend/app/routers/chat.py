import json
import logging
from uuid import UUID

import anyio
import openai
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app import context, llm
from app import repository as repo
from app.config import settings
from app.db import pool
from app.pricing import cost_usd
from app.schemas import ChatRequest

router = APIRouter(tags=["chat"])

# uvicorn's logger already prints to the terminal that runs the server.
logger = logging.getLogger("uvicorn.error")

def sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"

@router.post("/conversations/{conversation_id}/chat")
async def chat(conversation_id: UUID, body: ChatRequest):
    # Short transaction before streaming: check the conversation, save the user message, load the history.
    async with pool.connection() as conn:
        conversation = await repo.get_conversation(conn, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        await repo.add_message(conn, conversation_id, "user", body.content)
        history = await repo.list_messages(conn, conversation_id)

    model = conversation["model"]

    async def events():
        reply = ""
        usage = {}
        finish_reason = None
        completed = False
        try:
            # Choose what to send. Strategy B may call the cheap model here to fold old messages into the summary.
            messages, summary_update = await context.build_messages(conversation, history)
            if summary_update:
                async with pool.connection() as conn:
                    await repo.save_summary(conn, conversation_id, *summary_update)
            sent = {
                "strategy": settings.context_strategy,
                "messages_sent": len(messages) - 1,
                "messages_total": len(history),
                "estimated_tokens": context.count_tokens(messages),
            }
            logger.info("context %s: sending %d of %d messages, about %d tokens", *sent.values())

            async for kind, value in llm.stream_chat(model, messages):
                if kind == "token":
                    reply += value
                    yield sse({"type": "token", "text": value})
                elif kind == "usage":
                    usage = value
                elif kind == "finish":
                    finish_reason = value
            completed = True
        except openai.RateLimitError as exc:
            wait = exc.response.headers.get("retry-after", "a few")
            yield sse({"type": "error", "message": f"Groq rate limit reached. Try again in {wait} seconds."})
            return
        except Exception as exc:
            yield sse({"type": "error", "message": str(exc)})
            return
        finally:
            # Stopped by the client, or failed mid-reply: keep the text that was already streamed.
            if not completed and reply:
                with anyio.CancelScope(shield=True):
                    async with pool.connection() as conn:
                        await repo.add_message(conn, conversation_id, "assistant", reply, model=model)

        cost = cost_usd(model, usage["prompt_tokens"], usage["completion_tokens"]) if usage else None
        async with pool.connection() as conn:
            saved = await repo.add_message(
                conn,
                conversation_id,
                "assistant",
                reply,
                model=model,
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                reasoning_tokens=usage.get("reasoning_tokens"),
                cost_usd=cost,
            )

        # First reply in this chat: swap the placeholder title for a short one from the cheap model.
        # The frontend reloads the conversation list when the stream ends, so it picks up the new title.
        if len(history) == 1:
            try:
                title = await llm.make_title(body.content)
                if title:
                    async with pool.connection() as conn:
                        await repo.update_conversation(conn, conversation_id, title, None)
            except Exception as exc:
                logger.warning("auto-title failed, keeping the old title: %s", exc)

        yield sse({
            "type": "done",
            "message_id": saved["id"],
            "finish_reason": finish_reason,
            "usage": usage,
            "cost_usd": cost,
            "context": sent,
        })

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
