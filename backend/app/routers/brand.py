"""
Brand knowledge upload and management endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import pandas as pd
import logging
from pathlib import Path
import uuid
from datetime import datetime

from app.deps import get_db, get_ingestion_service
from app.services.rag.ingestion import IngestionService
from app.db.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/brand", tags=["brand"])


@router.post("/upload")
async def upload_brand_knowledge(
    files: List[UploadFile] = File(...),
    brand_id: Optional[str] = Form(None),
    brand_name: Optional[str] = Form(None),
    brand_column: Optional[str] = Form("brand"),
    text_column: Optional[str] = Form("text")
):
    """
    Upload brand knowledge files (CSV, XLSX, PDF, TXT).
    
    For CSV/XLSX: Expects columns for brand and text (configurable via brand_column/text_column).
    For PDF/TXT: Requires brand_id or brand_name to associate the entire document with a brand.
    """
    db: Database = await get_db()
    ingestion_service: IngestionService = get_ingestion_service()
    
    results = []
    start_time = datetime.utcnow()
    
    for file in files:
        try:
            file_ext = file.filename.split('.')[-1].lower() if file.filename else ""
            
            if file_ext in ['csv', 'xlsx', 'xls']:
                content = await file.read()
                
                if file_ext == 'csv':
                    df = pd.read_csv(pd.io.common.BytesIO(content))
                else:
                    df = pd.read_excel(pd.io.common.BytesIO(content))
                
                columns_lower = {col.lower(): col for col in df.columns}
                brand_col = columns_lower.get(brand_column.lower())
                text_col = columns_lower.get(text_column.lower())
                
                if not brand_col or not text_col:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Could not find columns '{brand_column}' and '{text_column}' in file {file.filename}. Available columns: {list(df.columns)}"
                    )
                
                brand_stats = {}
                for brand_value, group in df.groupby(brand_col):
                    brand_id_normalized = str(brand_value).lower().replace(' ', '_')
                    brand_name_normalized = str(brand_value)
                    
                    await db.create_brand(brand_id_normalized, brand_name_normalized)
                    
                    texts = group[text_col].dropna().tolist()
                    combined_text = "\n\n".join(str(t) for t in texts)
                    
                    doc_id = f"{brand_id_normalized}_{uuid.uuid4().hex[:8]}"
                    result = await ingestion_service.ingest_text(
                        text=combined_text,
                        brand_id=brand_id_normalized,
                        filename=f"{file.filename}_{brand_value}",
                        doc_id=doc_id
                    )
                    
                    brand_stats[brand_name_normalized] = {
                        "brand_id": brand_id_normalized,
                        "documents": 1,
                        "chunks": result['chunks'],
                        "vectors": result['vectors']
                    }
                
                results.append({
                    "filename": file.filename,
                    "file_type": file_ext,
                    "brands": brand_stats,
                    "status": "success"
                })
                
            elif file_ext in ['pdf', 'txt']:
                if not brand_id and not brand_name:
                    raise HTTPException(
                        status_code=400,
                        detail=f"brand_id or brand_name required for {file_ext.upper()} files"
                    )
                
                if not brand_id:
                    brand_id = brand_name.lower().replace(' ', '_')
                
                await db.create_brand(brand_id, brand_name or brand_id)
                
                content = await file.read()
                
                if file_ext == 'pdf':
                    result = await ingestion_service.ingest_pdf(
                        pdf_bytes=content,
                        brand_id=brand_id,
                        filename=file.filename
                    )
                else:  # txt
                    text = content.decode('utf-8')
                    result = await ingestion_service.ingest_text(
                        text=text,
                        brand_id=brand_id,
                        filename=file.filename
                    )
                
                results.append({
                    "filename": file.filename,
                    "file_type": file_ext,
                    "brand_id": brand_id,
                    "brand_name": brand_name or brand_id,
                    "documents": 1,
                    "chunks": result['chunks'],
                    "vectors": result['vectors'],
                    "status": "success"
                })
                
            else:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": f"Unsupported file type: {file_ext}"
                })
                
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    end_time = datetime.utcnow()
    duration_sec = (end_time - start_time).total_seconds()
    
    return {
        "status": "completed",
        "files_processed": len(files),
        "results": results,
        "duration_sec": duration_sec
    }


@router.get("/list")
async def list_brands():
    """List all brands with statistics."""
    db: Database = await get_db()
    brands = await db.list_brands_with_stats()
    
    return {
        "brands": brands,
        "total": len(brands)
    }


@router.post("/reindex")
async def reindex_brand(brand_id: str):
    """Rebuild FAISS index for a brand from stored documents."""
    db: Database = await get_db()
    ingestion_service: IngestionService = get_ingestion_service()
    
    brand = await db.get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")
    
    try:
        chunks = await db.get_brand_chunks(brand_id)
        
        if not chunks:
            return {
                "status": "success",
                "brand_id": brand_id,
                "message": "No chunks found to reindex"
            }
        
        texts = [chunk['content'] for chunk in chunks]
        metadatas = [{"chunk_id": chunk['id'], "brand_id": brand_id} for chunk in chunks]
        
        await db.delete_brand(brand_id)
        
        await db.create_brand(brand_id, brand['name'])
        
        result = await ingestion_service.reindex_brand(brand_id, texts, metadatas)
        
        return {
            "status": "success",
            "brand_id": brand_id,
            "chunks_reindexed": len(texts),
            "vectors_created": result['vectors']
        }
        
    except Exception as e:
        logger.error(f"Error reindexing brand {brand_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_brand_stats(brand_id: Optional[str] = None):
    """Get statistics for a specific brand or all brands."""
    db: Database = await get_db()
    
    if brand_id:
        brand = await db.get_brand(brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")
        
        chunks = await db.get_brand_chunks(brand_id)
        
        return {
            "brand_id": brand_id,
            "name": brand['name'],
            "documents": len(set(c['document_id'] for c in chunks)),
            "chunks": len(chunks),
            "vectors": len(chunks),  # Assuming 1 vector per chunk
            "last_ingested_at": brand['last_ingested_at']
        }
    else:
        brands = await db.list_brands_with_stats()
        return {"brands": brands}
