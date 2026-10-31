from uuid import UUID
from psycopg import AsyncConnection

async def list_conversations(conn: AsyncConnection) -> list[dict]:
    cur = await conn.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
    return await cur.fetchall()

async def get_conversation(conn: AsyncConnection, conversation_id: UUID) -> dict | None:
    cur = await conn.execute("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
    return await cur.fetchone()

async def create_conversation(conn: AsyncConnection, title: str, model: str, system_prompt: str) -> dict:
    cur = await conn.execute(
        """
        INSERT INTO conversations (title, model, system_prompt)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (title, model, system_prompt),
    )
    return await cur.fetchone()

async def update_conversation(
    conn: AsyncConnection, conversation_id: UUID, title: str | None, model: str | None
) -> dict | None:
    cur = await conn.execute(
        """
        UPDATE conversations
        SET title = COALESCE(%s, title),
            model = COALESCE(%s, model),
            updated_at = now()
        WHERE id = %s
        RETURNING *
        """,
        (title, model, conversation_id),
    )
    return await cur.fetchone()

async def delete_conversation(conn: AsyncConnection, conversation_id: UUID) -> bool:
    cur = await conn.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
    return cur.rowcount > 0

async def list_messages(conn: AsyncConnection, conversation_id: UUID) -> list[dict]:
    cur = await conn.execute(
        "SELECT * FROM messages WHERE conversation_id = %s ORDER BY id", (conversation_id,),
    )
    return await cur.fetchall()

async def add_message(
    conn: AsyncConnection,
    conversation_id: UUID,
    role: str,
    content: str,
    *,
    model: str | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    reasoning_tokens: int | None = None,
    cost_usd: float | None = None
) -> dict:
    cur = await conn.execute(
        """
        INSERT INTO messages
            (conversation_id, role, content, model, prompt_tokens, completion_tokens, reasoning_tokens, cost_usd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (conversation_id, role, content, model, prompt_tokens, completion_tokens, reasoning_tokens, cost_usd),
    )
    message = await cur.fetchone()
    await conn.execute("UPDATE conversations SET updated_at = now() WHERE id = %s", (conversation_id,))
    return message