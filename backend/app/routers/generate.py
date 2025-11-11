"""
Content generation router.
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

router = APIRouter(prefix="/api/generate", tags=["generate"])


class GenerateImageRequest(BaseModel):
    prompt: str
    brand_id: Optional[str] = None
    template_id: Optional[str] = None
    template_fields: Optional[dict] = None
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = None
    guidance_scale: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    seed: Optional[int] = None


class GenerateVideoRequest(BaseModel):
    prompt: str
    brand_id: Optional[str] = None
    template_id: Optional[str] = None
    template_fields: Optional[dict] = None
    num_frames: Optional[int] = None
    num_inference_steps: Optional[int] = None
    fps: Optional[int] = None
    seed: Optional[int] = None


class GenerateResponse(BaseModel):
    status: str
    media_url: Optional[str] = None
    filename: Optional[str] = None
    media_type: Optional[str] = None
    original_prompt: Optional[str] = None
    enhanced_prompt: Optional[str] = None
    error: Optional[str] = None


@router.post("/image", response_model=GenerateResponse)
async def generate_image(
    request: GenerateImageRequest,
    db = Depends(get_db),
    vector_adapter = Depends(get_vector_adapter),
    image_provider = Depends(get_image_provider),
    safety_service = Depends(get_safety_service),
    caption_service = Depends(get_caption_service)
):
    """Generate an image with optional brand context."""
    retrieval_service = RetrievalService(vector_adapter, db)
    prompt_composer = PromptComposer(retrieval_service)
    image_service = ImageGenerationService(
        image_provider, safety_service, caption_service, prompt_composer
    )
    
    template_prompt = None
    if request.template_id and request.template_fields:
        from app.services.rag.templates import TemplateService
        template_service = TemplateService()
        try:
            template_prompt = template_service.fill_template(request.template_id, request.template_fields)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    result = await image_service.generate(
        user_prompt=request.prompt,
        brand_id=request.brand_id,
        template_prompt=template_prompt,
        negative_prompt=request.negative_prompt,
        num_inference_steps=request.num_inference_steps,
        guidance_scale=request.guidance_scale,
        width=request.width,
        height=request.height,
        seed=request.seed
    )
    
    if result['status'] != 'success':
        return result
    
    return {
        "status": "success",
        "media_url": f"/media/{result['filename']}",
        "filename": result['filename'],
        "media_type": "image",
        "original_prompt": result.get('original_prompt', ''),
        "enhanced_prompt": result.get('enhanced_prompt', '')
    }


@router.post("/video", response_model=GenerateResponse)
async def generate_video(
    request: GenerateVideoRequest,
    db = Depends(get_db),
    vector_adapter = Depends(get_vector_adapter),
    video_provider = Depends(get_video_provider),
    safety_service = Depends(get_safety_service)
):
    """Generate a video with optional brand context."""
    retrieval_service = RetrievalService(vector_adapter, db)
    prompt_composer = PromptComposer(retrieval_service)
    video_service = VideoGenerationService(
        video_provider, safety_service, prompt_composer
    )
    
    template_prompt = None
    if request.template_id and request.template_fields:
        from app.services.rag.templates import TemplateService
        template_service = TemplateService()
        try:
            template_prompt = template_service.fill_template(request.template_id, request.template_fields)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    result = await video_service.generate(
        user_prompt=request.prompt,
        brand_id=request.brand_id,
        template_prompt=template_prompt,
        num_frames=request.num_frames,
        num_inference_steps=request.num_inference_steps,
        fps=request.fps,
        seed=request.seed
    )
    
    if result['status'] != 'success':
        return result
    
    return {
        "status": "success",
        "media_url": f"/media/{result['filename']}",
        "filename": result['filename'],
        "media_type": "video",
        "original_prompt": result.get('original_prompt', ''),
        "enhanced_prompt": result.get('enhanced_prompt', '')
    }
