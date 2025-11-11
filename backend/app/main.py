from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from typing import Optional

from app.models.schemas import (
    GenerateImageRequest,
    GenerateVideoRequest,
    ChatRequest,
    ChatMessage,
    BrandMetadataResponse,
    BrandsListResponse,
    UploadResponse
)
from app.services.vector_db import vector_db
from app.services.image_generator import image_generator
from app.services.video_generator import video_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Content Generation POC API")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

os.makedirs("./data/generated_content", exist_ok=True)
app.mount("/media", StaticFiles(directory="./data/generated_content"), name="media")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/brands/upload")
async def upload_brand_metadata(
    file: UploadFile = File(...),
    brand_name: str = None
):
    """
    Upload brand metadata CSV or Excel file.
    """
    if not brand_name:
        raise HTTPException(status_code=400, detail="brand_name is required")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(
            status_code=400,
            detail="File must be CSV or Excel format (.csv, .xlsx, .xls)"
        )
    
    os.makedirs("./data/brand_metadata", exist_ok=True)
    temp_path = f"./data/brand_metadata/{file.filename}"
    
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        if file_ext == 'csv':
            records = vector_db.ingest_brand_metadata(temp_path, brand_name)
        else:
            records = vector_db.ingest_brand_metadata_excel(temp_path, brand_name)
        
        return UploadResponse(
            status="success",
            message=f"Successfully ingested {records} records for brand '{brand_name}'",
            brand_name=brand_name,
            records_ingested=records
        )
        
    except Exception as e:
        logger.error(f"Error uploading brand metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brands", response_model=BrandsListResponse)
async def list_brands():
    """
    List all brands in the vector database.
    """
    brands = vector_db.list_brands()
    return BrandsListResponse(brands=brands)

@app.get("/api/brands/{brand_name}", response_model=BrandMetadataResponse)
async def get_brand_metadata(brand_name: str):
    """
    Get metadata for a specific brand.
    """
    metadata = vector_db.retrieve_brand_metadata(brand_name)
    
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Brand '{brand_name}' not found in database"
        )
    
    return BrandMetadataResponse(
        brand_name=brand_name,
        metadata=metadata
    )

@app.delete("/api/brands/{brand_name}")
async def delete_brand(brand_name: str):
    """
    Delete a brand and all its metadata.
    """
    deleted_count = vector_db.delete_brand(brand_name)
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Brand '{brand_name}' not found in database"
        )
    
    return {
        "status": "success",
        "message": f"Deleted {deleted_count} records for brand '{brand_name}'"
    }

@app.post("/api/generate/image")
async def generate_image(request: GenerateImageRequest):
    """
    Generate an image using Stable Diffusion XL with RAG-enhanced prompts.
    """
    brand_metadata = None
    
    if request.brand_name:
        brand_metadata = vector_db.retrieve_brand_metadata(request.brand_name)
        
        if not brand_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Brand '{request.brand_name}' not found. Please upload brand metadata first."
            )
    
    result = image_generator.generate_image(
        prompt=request.prompt,
        brand_metadata=brand_metadata,
        negative_prompt=request.negative_prompt,
        num_inference_steps=request.num_inference_steps,
        guidance_scale=request.guidance_scale,
        width=request.width,
        height=request.height
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    media_url = f"/media/{result['filename']}"
    
    return {
        "status": "success",
        "media_url": media_url,
        "filename": result["filename"],
        "prompt": result["prompt"],
        "original_prompt": result["original_prompt"]
    }

@app.post("/api/generate/video")
async def generate_video(request: GenerateVideoRequest):
    """
    Generate a video using ModelScope text-to-video with RAG-enhanced prompts.
    """
    brand_metadata = None
    
    if request.brand_name:
        brand_metadata = vector_db.retrieve_brand_metadata(request.brand_name)
        
        if not brand_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Brand '{request.brand_name}' not found. Please upload brand metadata first."
            )
    
    result = video_generator.generate_video(
        prompt=request.prompt,
        brand_metadata=brand_metadata,
        negative_prompt=request.negative_prompt,
        num_inference_steps=request.num_inference_steps,
        num_frames=request.num_frames,
        guidance_scale=request.guidance_scale
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    media_url = f"/media/{result['filename']}"
    
    return {
        "status": "success",
        "media_url": media_url,
        "filename": result["filename"],
        "prompt": result["prompt"],
        "original_prompt": result["original_prompt"],
        "num_frames": result.get("num_frames", 0)
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint that generates content based on user message.
    """
    brand_metadata = None
    
    if request.brand_name:
        brand_metadata = vector_db.retrieve_brand_metadata(request.brand_name)
        
        if not brand_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Brand '{request.brand_name}' not found. Please upload brand metadata first."
            )
    
    if request.generation_type == "image":
        result = image_generator.generate_image(
            prompt=request.message,
            brand_metadata=brand_metadata
        )
    elif request.generation_type == "video":
        result = video_generator.generate_video(
            prompt=request.message,
            brand_metadata=brand_metadata
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="generation_type must be 'image' or 'video'"
        )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    media_url = f"/media/{result['filename']}"
    media_type = "image" if request.generation_type == "image" else "video"
    
    return {
        "status": "success",
        "message": f"Generated {media_type} for: {request.message}",
        "media_url": media_url,
        "media_type": media_type,
        "filename": result["filename"],
        "enhanced_prompt": result["prompt"]
    }
