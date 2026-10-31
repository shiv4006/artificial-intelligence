import json
import anyio
import openai
from uuid import UUID


from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app import llm
from app import repository as repo
from app.db import pool
from app.pricing import cost_usd
from app.schemas import ChatRequest

router = APIRouter(tags=["chat"])

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
    messages = [{"role": "system", "content": conversation["system_prompt"]}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history]
    
    async def events():
        reply = ""
        usage = {}
        finish_reason = None
        completed = False
        try:
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
        
        yield sse({
            "type": "done",
            "message_id": saved["id"],
            "finish_reason": finish_reason,
            "usage": usage,
            "cost_usd": cost,
        })
    
    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )