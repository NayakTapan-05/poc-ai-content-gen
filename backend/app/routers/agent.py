"""
Agent router for intelligent chat-based content generation.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from app.deps import (
    get_db, get_vector_adapter, get_image_provider, get_video_provider,
    get_safety_service, get_caption_service
)
from app.services.rag.retrieval import RetrievalService
from app.services.generation.compose import PromptComposer
from app.services.generation.image import ImageGenerationService
from app.services.generation.video import VideoGenerationService
from app.services.agent.intent import IntentDetector
from app.services.agent.router import AgentRouter

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    session_id: str
    brand_id: Optional[str] = None


class ChatResponse(BaseModel):
    status: str
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    intent: Optional[str] = None
    error: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db = Depends(get_db),
    vector_adapter = Depends(get_vector_adapter),
    image_provider = Depends(get_image_provider),
    video_provider = Depends(get_video_provider),
    safety_service = Depends(get_safety_service),
    caption_service = Depends(get_caption_service)
):
    """
    Intelligent chat endpoint that routes to appropriate handler.
    Supports Q&A, image generation, video generation, and refinement.
    """
    session = await db.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.add_message(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    
    messages = await db.get_messages(request.session_id, limit=10)
    has_previous_generation = any(
        msg.get('media_url') for msg in messages if msg.get('role') == 'assistant'
    )
    
    retrieval_service = RetrievalService(vector_adapter, db)
    prompt_composer = PromptComposer(retrieval_service)
    
    image_service = ImageGenerationService(
        image_provider, safety_service, caption_service, prompt_composer
    )
    video_service = VideoGenerationService(
        video_provider, safety_service, prompt_composer
    )
    
    intent_detector = IntentDetector()
    agent_router = AgentRouter(
        intent_detector, retrieval_service, image_service, video_service
    )
    
    result = await agent_router.route(
        message=request.message,
        brand_id=request.brand_id,
        session_id=request.session_id,
        has_previous_generation=has_previous_generation
    )
    
    await db.add_message(
        session_id=request.session_id,
        role="assistant",
        content=result.get('content', ''),
        media_url=result.get('media_url'),
        media_type=result.get('media_type')
    )
    
    return result
