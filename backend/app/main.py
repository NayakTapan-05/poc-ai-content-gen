from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from app.services.hf_generator import HFGenerator
    from app.services.faiss_rag import FAISSRAGService
    from app.services.brand_uploader import BrandUploader
    hf_available = True
except Exception as e:
    logging.warning(f"HF services not available: {e}")
    hf_available = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Content Generation POC API")

if hf_available:
    try:
        hf_generator = HFGenerator()
        faiss_rag = FAISSRAGService()
        brand_uploader = BrandUploader()
    except Exception as e:
        logger.warning(f"Failed to initialize HF services: {e}")
        hf_available = False

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


@app.get("/api/models")
async def get_models():
    """
    Get available models for image and video generation
    """
    if not hf_available:
        return JSONResponse(
            status_code=503,
            content={"error": "HF services not available"}
        )
    
    try:
        models = hf_generator.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_content(
    type: str = Form(...),
    prompt: str = Form(...),
    model_id: str = Form(None),
    brand_name: str = Form(None),
    seed: int = Form(None),
    steps: int = Form(None),
    width: int = Form(None),
    height: int = Form(None),
    image: UploadFile = File(None)
):
    """
    Unified generation endpoint for both image and video
    Supports HF Inference API with local diffusers fallback
    """
    if not hf_available:
        return JSONResponse(
            status_code=503,
            content={"error": "HF services not available"}
        )
    
    try:
        enhanced_prompt = prompt
        if brand_name:
            results = faiss_rag.search(brand_name, prompt, top_k=3)
            if results:
                context = "\n".join([r["text"] for r in results[:3]])
                enhanced_prompt = f"{prompt}\n\nBrand context: {context}"
        
        if type == "image":
            result = hf_generator.generate_image(
                prompt=enhanced_prompt,
                model_id=model_id or "sd-turbo",
                width=width or 768,
                height=height or 768,
                num_inference_steps=steps or 4,
                seed=seed
            )
        elif type == "video":
            image_bytes = None
            if image:
                image_bytes = await image.read()
            
            result = hf_generator.generate_video(
                prompt=enhanced_prompt,
                model_id=model_id or "svd-img2vid",
                image=image_bytes,
                num_frames=12,
                num_inference_steps=steps or 8,
                seed=seed
            )
        else:
            raise HTTPException(status_code=400, detail="type must be 'image' or 'video'")
        
        return result
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Generation failed: {str(e)}. Please check HF_TOKEN and model configuration."
        )

@app.get("/api/templates")
async def get_templates(type: Optional[str] = None):
    """
    Get template catalog for content generation
    """
    try:
        templates_path = Path("./data/templates/templates.json")
        
        if not templates_path.exists():
            return []
        
        with open(templates_path, "r") as f:
            templates = json.load(f)
        
        if type:
            templates = [t for t in templates if t.get("type") == type]
        
        return templates
    
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """
    Get specific template by ID
    """
    try:
        templates_path = Path("./data/templates/templates.json")
        
        if not templates_path.exists():
            raise HTTPException(status_code=404, detail="Templates not found")
        
        with open(templates_path, "r") as f:
            templates = json.load(f)
        
        template = next((t for t in templates if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
        
        return template
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brand/upload")
async def upload_brand_data(
    file: UploadFile = File(...),
    brand_name: str = Form(None),
    brand_col: str = Form("brand"),
    text_col: str = Form("text")
):
    """
    Upload brand data (CSV/XLSX/PDF/TXT) and ingest into FAISS
    """
    if not hf_available:
        return JSONResponse(
            status_code=503,
            content={"error": "HF services not available"}
        )
    
    try:
        file_content = await file.read()
        filename = file.filename or "upload"
        
        if filename.endswith('.csv') or filename.endswith('.xlsx'):
            result = brand_uploader.process_csv_xlsx(
                file_content=file_content,
                filename=filename,
                brand_col=brand_col,
                text_col=text_col
            )
        elif filename.endswith('.pdf'):
            if not brand_name:
                raise HTTPException(status_code=400, detail="brand_name required for PDF upload")
            result = brand_uploader.process_pdf(
                file_content=file_content,
                filename=filename,
                brand_name=brand_name
            )
        elif filename.endswith('.txt'):
            if not brand_name:
                raise HTTPException(status_code=400, detail="brand_name required for TXT upload")
            result = brand_uploader.process_txt(
                file_content=file_content,
                filename=filename,
                brand_name=brand_name
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV, XLSX, PDF, or TXT")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brand/list")
async def list_brands_faiss():
    """
    List all brands in FAISS vector database
    """
    if not hf_available:
        return JSONResponse(
            status_code=503,
            content={"error": "HF services not available"}
        )
    
    try:
        brands = faiss_rag.list_brands()
        return {"brands": brands}
    except Exception as e:
        logger.error(f"Error listing brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/stats")
async def get_rag_stats(brandId: str):
    """
    Get RAG statistics for a specific brand
    """
    if not hf_available:
        return JSONResponse(
            status_code=503,
            content={"error": "HF services not available"}
        )
    
    try:
        stats = faiss_rag.get_brand_stats(brandId)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
