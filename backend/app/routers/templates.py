"""
Templates router for content generation templates.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.services.rag.templates import TemplateService

router = APIRouter(prefix="/api/templates", tags=["templates"])

template_service = TemplateService()


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    type: str
    fields: List[Dict]


class FillTemplateRequest(BaseModel):
    template_id: str
    fields: Dict[str, str]


class FillTemplateResponse(BaseModel):
    template_id: str
    filled_prompt: str


@router.get("", response_model=List[TemplateResponse])
async def list_templates(content_type: Optional[str] = None):
    """List all available templates."""
    templates = template_service.list_templates(content_type)
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific template."""
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/fill", response_model=FillTemplateResponse)
async def fill_template(request: FillTemplateRequest):
    """Fill a template with provided fields."""
    try:
        filled_prompt = template_service.fill_template(request.template_id, request.fields)
        return {
            "template_id": request.template_id,
            "filled_prompt": filled_prompt
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
