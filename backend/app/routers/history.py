"""
Chat history router.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from app.deps import get_db

router = APIRouter(prefix="/api/history", tags=["history"])


class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    timestamp: str


@router.get("/{session_id}", response_model=List[MessageResponse])
async def get_session_history(session_id: str, limit: Optional[int] = None, db = Depends(get_db)):
    """Get chat history for a session."""
    messages = await db.get_messages(session_id, limit)
    return messages
