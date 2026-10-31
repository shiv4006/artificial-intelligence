from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app import repository as repo
from app.db import pool
from app.schemas import Conversation, ConversationCreate, ConversationDetail, ConversationUpdate

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("", response_model=list[Conversation])
async def list_conversations():
    async with pool.connection() as conn:
        return await repo.list_conversations(conn)
    
@router.post("", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(body: ConversationCreate):
    async with pool.connection() as conn:
        return await repo.create_conversation(conn, body.title, body.model, body.system_prompt)
    
@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: UUID):
    async with pool.connection() as conn:
        conversation = await repo.get_conversation(conn, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        messages = await repo.list_messages(conn, conversation_id)
    return {**conversation, "messages": messages}

@router.patch("/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: UUID, body: ConversationUpdate):
    async with pool.connection() as conn:
        conversation = await repo.update_conversation(conn, conversation_id, body.title, body.model)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: UUID):
    async with pool.connection() as conn:
        deleted = await repo.delete_conversation(conn, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")