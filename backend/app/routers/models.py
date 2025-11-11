"""
Model selection and configuration endpoints.
"""
from fastapi import APIRouter
import torch
import logging

from app import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
async def get_available_models():
    """
    Get available models for image and video generation.
    Returns model options with device compatibility and defaults.
    """
    gpu_available = torch.cuda.is_available() and config.USE_GPU_IF_AVAILABLE
    
    image_models = [
        {
            "id": "sd-turbo",
            "label": "Stable Diffusion Turbo (Fast)",
            "device": "gpu|cpu",
            "description": "Fast generation with good quality",
            "recommended": True if gpu_available else False
        },
        {
            "id": "sd15",
            "label": "Stable Diffusion 1.5",
            "device": "gpu|cpu",
            "description": "Balanced quality and speed",
            "recommended": False
        },
        {
            "id": "sd-onnx",
            "label": "Stable Diffusion ONNX (CPU)",
            "device": "cpu",
            "description": "CPU-optimized model (slower but works without GPU)",
            "recommended": True if not gpu_available else False
        }
    ]
    
    video_models = [
        {
            "id": "svd-xt",
            "label": "Stable Video Diffusion XT",
            "device": "gpu|cpu",
            "description": "High-quality video generation (GPU fast, CPU slower)",
            "recommended": True
        }
    ]
    
    default_image = config.IMAGE_MODEL if config.IMAGE_MODEL else ("sd-turbo" if gpu_available else "sd-onnx")
    default_video = config.VIDEO_MODEL if config.VIDEO_MODEL else "svd-xt"
    
    return {
        "image": image_models,
        "video": video_models,
        "defaults": {
            "image_id": default_image,
            "video_id": default_video
        },
        "gpu_available": gpu_available,
        "current_device": "cuda" if gpu_available else "cpu"
    }


@router.get("/config")
async def get_model_config():
    """Get current model configuration from environment."""
    gpu_available = torch.cuda.is_available() and config.USE_GPU_IF_AVAILABLE
    
    return {
        "image_model": config.IMAGE_MODEL,
        "video_model": config.VIDEO_MODEL,
        "embeddings_model": config.EMBEDDINGS_MODEL,
        "caption_model": config.CAPTION_MODEL,
        "gpu_available": gpu_available,
        "device": "cuda" if gpu_available else "cpu",
        "image_settings": {
            "size": config.IMAGE_SIZE,
            "steps": config.IMAGE_STEPS,
            "guidance_scale": config.IMAGE_GUIDANCE_SCALE
        },
        "video_settings": {
            "resolution": config.VIDEO_RES,
            "frames": config.VIDEO_FRAMES,
            "steps": config.VIDEO_STEPS,
            "fps": config.VIDEO_FPS,
            "seconds": config.VIDEO_SECONDS
        }
    }
