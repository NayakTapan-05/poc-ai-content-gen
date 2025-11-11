"""
Configuration management for the application.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))

API_PORT = int(os.getenv("API_PORT", "8000"))
WEB_PORT = int(os.getenv("WEB_PORT", "3000"))

USE_GPU_IF_AVAILABLE = os.getenv("USE_GPU_IF_AVAILABLE", "true").lower() == "true"

IMAGE_MODEL = os.getenv("IMAGE_MODEL", "sd-turbo")  # sd-turbo, sd15, onnx
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "svd-xt")  # svd-xt
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
CAPTION_MODEL = os.getenv("CAPTION_MODEL", "blip-base")

RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "900"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "256"))
IMAGE_STEPS = int(os.getenv("IMAGE_STEPS", "8"))
IMAGE_GUIDANCE_SCALE = float(os.getenv("IMAGE_GUIDANCE_SCALE", "7.5"))

VIDEO_RES = int(os.getenv("VIDEO_RES", "256"))
VIDEO_FRAMES = int(os.getenv("VIDEO_FRAMES", "8"))
VIDEO_STEPS = int(os.getenv("VIDEO_STEPS", "8"))
VIDEO_SECONDS = int(os.getenv("VIDEO_SECONDS", "2"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "8"))

TEST_TIMEOUT_SEC = int(os.getenv("TEST_TIMEOUT_SEC", "1800"))

ENABLE_SAFETY_CHECKS = os.getenv("ENABLE_SAFETY_CHECKS", "true").lower() == "true"
ENABLE_WATERMARK = os.getenv("ENABLE_WATERMARK", "true").lower() == "true"

DATABASE_PATH = DATA_DIR / "app.db"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

VECTORS_DIR = DATA_DIR / "vectors"
INGEST_DIR = DATA_DIR / "ingest"
GENERATED_DIR = DATA_DIR / "generated_content"

for dir_path in [DATA_DIR, VECTORS_DIR, INGEST_DIR, GENERATED_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
