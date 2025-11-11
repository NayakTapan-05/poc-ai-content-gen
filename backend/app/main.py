"""
Main FastAPI application for AI Content Generation POC.
Local-first with real OSS models, RAG, multi-session chat.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app import config
from app.deps import get_db
from app.routers import session, history, templates, rag, generate, agent, brand, models

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    logger.info("Starting AI Content Generation POC")
    logger.info(f"Data directory: {config.DATA_DIR}")
    logger.info(f"GPU available: {config.USE_GPU_IF_AVAILABLE}")
    
    db = await get_db()
    logger.info("Database initialized")
    
    yield
    
    logger.info("Shutting down AI Content Generation POC")


app = FastAPI(
    title="AI Content Generation POC",
    description="Local-first AI content generation with RAG and multi-session chat",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(config.GENERATED_DIR)), name="media")

app.include_router(session.router)
app.include_router(history.router)
app.include_router(templates.router)
app.include_router(rag.router)
app.include_router(generate.router)
app.include_router(agent.router)
app.include_router(brand.router)
app.include_router(models.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Content Generation POC",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Multi-session chat",
            "RAG with FAISS + sentence-transformers",
            "Local image generation (SD-Turbo/SD1.5/ONNX)",
            "Local video generation (Stable Video Diffusion)",
            "Safety checks (Detoxify + NudeNet)",
            "Template-first generation",
            "GPU/CPU auto-detection"
        ]
    }


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Get public configuration."""
    return {
        "image_model": config.IMAGE_MODEL,
        "video_model": config.VIDEO_MODEL,
        "embeddings_model": config.EMBEDDINGS_MODEL,
        "gpu_available": config.USE_GPU_IF_AVAILABLE,
        "safety_enabled": config.ENABLE_SAFETY_CHECKS,
        "image_size": config.IMAGE_SIZE,
        "video_frames": config.VIDEO_FRAMES
    }
