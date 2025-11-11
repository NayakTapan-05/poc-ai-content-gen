"""
Session management router.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
import uuid

from app.deps import get_db

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    name: str


class SessionResponse(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str


@router.post("", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest, db = Depends(get_db)):
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    session = await db.create_session(session_id, request.name)
    return session


@router.get("", response_model=List[SessionResponse])
async def list_sessions(db = Depends(get_db)):
    """List all chat sessions."""
    sessions = await db.list_sessions()
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db = Depends(get_db)):
    """Get a specific session."""
    session = await db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}")
async def delete_session(session_id: str, db = Depends(get_db)):
    """Delete a session."""
    deleted = await db.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": "Session deleted"}
