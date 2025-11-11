"""
RAG (Retrieval-Augmented Generation) router.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import uuid

from app import config
from app.deps import get_db, get_vector_adapter
from app.services.rag.ingestion import IngestionService
from app.services.rag.retrieval import RetrievalService

router = APIRouter(prefix="/api/rag", tags=["rag"])


class IngestResponse(BaseModel):
    status: str
    brand_id: str
    files_processed: int
    total_chunks: int
    total_vectors: int


class BrandListResponse(BaseModel):
    brands: List[str]


class RetrievalRequest(BaseModel):
    brand_id: str
    query: str
    top_k: Optional[int] = 5


class RetrievalResponse(BaseModel):
    brand_id: str
    query: str
    results: List[dict]


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    brand_id: str,
    files: List[UploadFile] = File(...),
    db = Depends(get_db),
    vector_adapter = Depends(get_vector_adapter)
):
    """
    Ingest documents for a brand into the RAG pipeline.
    Supports PDF, DOCX, TXT, CSV files.
    """
    if not brand_id:
        raise HTTPException(status_code=400, detail="brand_id is required")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    brand_dir = config.INGEST_DIR / brand_id
    brand_dir.mkdir(parents=True, exist_ok=True)
    
    file_paths = []
    for file in files:
        if not file.filename:
            continue
        
        file_path = brand_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(file_path)
    
    ingestion_service = IngestionService(vector_adapter, db)
    result = await ingestion_service.ingest_files(file_paths, brand_id)
    
    return {
        "status": "success",
        **result
    }


@router.get("/brands", response_model=BrandListResponse)
async def list_brands(db = Depends(get_db)):
    """List all brands with ingested data."""
    brands = await db.list_brands()
    return {"brands": brands}


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_context(
    request: RetrievalRequest,
    db = Depends(get_db),
    vector_adapter = Depends(get_vector_adapter)
):
    """Retrieve relevant context for a brand and query."""
    retrieval_service = RetrievalService(vector_adapter, db)
    results = retrieval_service.retrieve(request.brand_id, request.query, request.top_k)
    
    return {
        "brand_id": request.brand_id,
        "query": request.query,
        "results": results
    }


@router.delete("/brands/{brand_id}")
async def delete_brand(
    brand_id: str,
    db = Depends(get_db),
    vector_adapter = Depends(get_vector_adapter)
):
    """Delete all data for a brand."""
    vector_adapter.delete_brand(brand_id)
    
    deleted_count = await db.delete_brand(brand_id)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    return {
        "status": "success",
        "message": f"Deleted brand: {brand_id}",
        "records_deleted": deleted_count
    }
