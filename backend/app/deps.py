"""
Dependency injection for FastAPI.
Provides singleton instances of services and adapters.
"""
import torch
import logging
from functools import lru_cache

from app import config

logger = logging.getLogger(__name__)

DEVICE = "cuda" if torch.cuda.is_available() and config.USE_GPU_IF_AVAILABLE else "cpu"
logger.info(f"Using device: {DEVICE} (GPU available: {torch.cuda.is_available()}, USE_GPU_IF_AVAILABLE: {config.USE_GPU_IF_AVAILABLE})")

_embeddings_adapter = None
_vector_adapter = None
_image_provider = None
_video_provider = None
_safety_service = None
_caption_service = None
_db_connection = None


@lru_cache(maxsize=1)
def get_embeddings_adapter():
    """Get or create embeddings adapter singleton."""
    global _embeddings_adapter
    if _embeddings_adapter is None:
        from app.adapters.embeddings_local import LocalEmbeddingsAdapter
        _embeddings_adapter = LocalEmbeddingsAdapter(
            model_name=config.EMBEDDINGS_MODEL,
            device=DEVICE
        )
    return _embeddings_adapter


@lru_cache(maxsize=1)
def get_vector_adapter():
    """Get or create vector store adapter singleton."""
    global _vector_adapter
    if _vector_adapter is None:
        from app.adapters.vector_faiss import FAISSVectorAdapter
        _vector_adapter = FAISSVectorAdapter(
            embeddings_adapter=get_embeddings_adapter(),
            persist_dir=config.VECTORS_DIR
        )
    return _vector_adapter


@lru_cache(maxsize=1)
def get_image_provider():
    """Get or create image provider singleton."""
    global _image_provider
    if _image_provider is None:
        from app.adapters.image_provider_local import LocalImageProvider
        _image_provider = LocalImageProvider(
            model_name=config.IMAGE_MODEL,
            device=DEVICE,
            output_dir=config.GENERATED_DIR
        )
    return _image_provider


@lru_cache(maxsize=1)
def get_video_provider():
    """Get or create video provider singleton."""
    global _video_provider
    if _video_provider is None:
        from app.adapters.video_provider_local import LocalVideoProvider
        _video_provider = LocalVideoProvider(
            model_name=config.VIDEO_MODEL,
            device=DEVICE,
            output_dir=config.GENERATED_DIR
        )
    return _video_provider


@lru_cache(maxsize=1)
def get_safety_service():
    """Get or create safety service singleton."""
    global _safety_service
    if _safety_service is None:
        from app.services.safety import SafetyService
        _safety_service = SafetyService(device=DEVICE)
    return _safety_service


@lru_cache(maxsize=1)
def get_caption_service():
    """Get or create caption service singleton."""
    global _caption_service
    if _caption_service is None:
        from app.adapters.caption_local import LocalCaptionAdapter
        _caption_service = LocalCaptionAdapter(
            model_name=config.CAPTION_MODEL,
            device=DEVICE
        )
    return _caption_service


async def get_db():
    """Get database connection."""
    global _db_connection
    if _db_connection is None:
        from app.db.database import Database
        _db_connection = Database(config.DATABASE_PATH)
        await _db_connection.init_db()
    return _db_connection


async def get_ingestion_service():
    """Get ingestion service instance."""
    from app.services.rag.ingestion import IngestionService
    vector_adapter = get_vector_adapter()
    db = await get_db()
    return IngestionService(vector_adapter, db)


def get_retrieval_service():
    """Get retrieval service instance."""
    from app.services.rag.retrieval import RetrievalService
    vector_adapter = get_vector_adapter()
    return RetrievalService(vector_adapter)
