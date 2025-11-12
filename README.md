# AI Content Generation POC with RAG Pipeline

A proof-of-concept application for AI-powered image and video generation with Retrieval-Augmented Generation (RAG) pipeline for brand-compliant content creation.

## Overview

This POC demonstrates a complete AI content generation system with **two user interfaces**:

### 🎨 Streamlit UI (NEW - HF-Focused)
- **Hugging Face Inference API** for fast, cloud-based generation
- **FAISS** vector database for brand metadata
- **Floating Action Button (FAB)** with template picker
- **Chat interface** with multi-turn conversations
- **Brand data upload** (CSV/XLSX/PDF/TXT)
- **Runtime model selection** (2 image + 2 video models)
- **Local diffusers fallback** when HF unavailable

### 🌐 React UI (Original)
- **ChromaDB** vector database for storing brand metadata
- **Stable Diffusion XL** for image generation
- **ModelScope Text-to-Video** for video generation
- **RAG Pipeline** to enhance prompts with brand-specific metadata
- **React + TypeScript** frontend with chat interface
- **FastAPI** backend with RESTful API

## Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **ChromaDB** - Vector database for brand metadata storage
- **Stable Diffusion XL** - Open-source image generation model
- **ModelScope** - Open-source text-to-video model
- **RAG Pipeline** - Retrieves brand metadata and enhances prompts

### Frontend
- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Pre-built UI components
- **React Router** - Client-side routing
- **Axios** - HTTP client

## Features

### Core Functionality
1. **Two Generation Modes**
   - Image Generation (Stable Diffusion XL)
   - Video Generation (ModelScope)

2. **Chat Interface**
   - Interactive conversation-based content generation
   - Real-time generation status
   - Content preview and download

3. **RAG Pipeline**
   - Upload brand metadata (CSV/Excel)
   - Automatic brand metadata retrieval
   - Prompt enhancement with brand context

4. **Brand Management**
   - Upload brand metadata files
   - List available brands
   - Select brand for generation
   - Delete brand data

## Quick Start (Streamlit UI)

### Prerequisites
- Python 3.10 or higher
- Poetry (Python package manager)
- Hugging Face account and token (see [SETUP_HF.md](SETUP_HF.md))

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/NayakTapan-05/poc-ai-content-gen.git
cd poc-ai-content-gen
```

2. **Set up Hugging Face token** (see [SETUP_HF.md](SETUP_HF.md)):
```bash
cd backend
cp .env.example .env
# Edit .env and add your HF_TOKEN
```

3. **Install dependencies**:
```bash
poetry install
```

4. **Run the Streamlit app**:
```bash
streamlit run apps/streamlit_app.py
```

5. **Open your browser**: http://localhost:8501

The backend API will start automatically on port 8000.

## Full Setup Instructions (Both UIs)

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher (for React UI)
- Poetry (Python package manager)
- npm or yarn (for React UI)
- CUDA-compatible GPU (recommended for faster generation)
- Hugging Face account and token (for Streamlit UI)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Start the backend server:
```bash
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`

**Note**: The first time you generate content, the AI models will be downloaded automatically. This may take several minutes and requires significant disk space (~10GB for Stable Diffusion XL, ~5GB for ModelScope).

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Streamlit UI

#### 1. Chat Interface
- Navigate to the **💬 Chat** page
- Type your request: "Generate an image of a sunset" or "Create a video for Dove brand"
- The bot will detect intent and open the template picker
- Or click the **➕ FAB button** (bottom-right) to manually open the template picker

#### 2. Template Picker
- Select **Image** or **Video** tab
- Choose a template (Product Hero, Lifestyle, Social Media, etc.)
- Fill in the template fields
- Optionally select a brand for RAG-enhanced prompts
- Click **Generate**

#### 3. Brand Data Upload
- Navigate to the **📁 Brand Data** page
- Upload CSV/XLSX (with column mapping), PDF, or TXT files
- View per-brand statistics (document count, vector count)

#### 4. Settings
- Navigate to the **⚙️ Settings** page
- View available models (2 image + 2 video)
- Configure generation parameters
- View environment configuration

#### 5. Model Selection
**Image Models**:
- `sd-turbo` - Stable Diffusion Turbo (fast, 4 steps)
- `sd15` - Stable Diffusion 1.5 (higher quality, more steps)

**Video Models**:
- `svd-img2vid` - Stable Video Diffusion (img2vid)
- `svd-xt` - Stable Video Diffusion (img2vid-xt, extended)

### React UI

#### 1. Upload Brand Metadata (Optional)

Before generating content, you can upload brand metadata to enable RAG-enhanced prompts.

**Brand Metadata Format (CSV/Excel)**:
```csv
brand_key,brand_value
tone_of_voice,Warm and caring
brand_communications,Emphasizes real beauty and self-confidence
visual_style,Natural and authentic
color_palette,Soft whites and blues
target_audience,Women of all ages
brand_values,Inclusivity and empowerment
messaging_style,Positive and uplifting
imagery_focus,Real people in everyday situations
```

**Upload via API**:
```bash
curl -X POST "http://localhost:8000/api/brands/upload?brand_name=Dove" \
  -F "file=@dove_metadata.csv"
```

A sample template is provided at `backend/data/brand_metadata/sample_brand_template.csv`

### 2. Generate Content

1. Open the frontend at `http://localhost:5173`
2. Click on either "Image Generation" or "Video Generation" tile
3. (Optional) Select a brand from the dropdown if you've uploaded brand metadata
4. Type your prompt in the chat interface
5. Press Enter or click Send
6. Wait for the AI to generate your content
7. Download the generated content using the download button

### 3. Example Prompts

**Without Brand Context**:
- "A beautiful sunset over the ocean"
- "A person running in a park"

**With Brand Context** (e.g., Dove):
- "Make me a campaign image for Dove brand"
- "Create a video showing real beauty"

The RAG pipeline will automatically enhance your prompt with brand-specific metadata like tone of voice, visual style, and color palette.

## API Endpoints

### Streamlit-Focused Endpoints (NEW)
- `GET /api/models` - Get available models (2 image + 2 video)
- `POST /api/generate` - Unified generation endpoint (image/video)
- `GET /api/templates` - Get template catalog
- `GET /api/templates/{id}` - Get specific template
- `POST /api/brand/upload` - Upload brand data (CSV/XLSX/PDF/TXT)
- `GET /api/brand/list` - List all brands (FAISS)
- `GET /api/rag/stats?brandId=` - Get per-brand RAG statistics

### React UI Endpoints (Original)
- `POST /api/brands/upload` - Upload brand metadata CSV/Excel
- `GET /api/brands` - List all brands (ChromaDB)
- `GET /api/brands/{brand_name}` - Get brand metadata
- `DELETE /api/brands/{brand_name}` - Delete brand
- `POST /api/generate/image` - Generate image
- `POST /api/generate/video` - Generate video
- `POST /api/chat` - Chat-based generation

### Health Check
- `GET /healthz` - Health check endpoint

### API Documentation
Interactive API documentation is available at `http://localhost:8000/docs`

## Project Structure

```
poc-ai-content-gen/
├── apps/
│   └── streamlit_app.py            # NEW: Streamlit UI
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application (extended)
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   ├── hf_generator.py     # NEW: HF Inference API
│   │   │   ├── faiss_rag.py        # NEW: FAISS RAG service
│   │   │   ├── brand_uploader.py   # NEW: Brand data ingestion
│   │   │   ├── vector_db.py        # ChromaDB service (React UI)
│   │   │   ├── image_generator.py  # Stable Diffusion XL (React UI)
│   │   │   └── video_generator.py  # ModelScope (React UI)
│   │   └── utils/
│   ├── data/
│   │   ├── templates/              # NEW: Template catalog
│   │   ├── vectors/                # NEW: FAISS indices
│   │   ├── ingest/                 # NEW: Ingested brand data
│   │   ├── brand_metadata/         # Uploaded brand files (React UI)
│   │   ├── generated_content/      # Generated images/videos
│   │   └── chroma_db/              # ChromaDB storage (React UI)
│   ├── .env.example                # NEW: Environment template
│   ├── pyproject.toml              # Python dependencies
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx     # Home page with tiles
│   │   │   └── ChatPage.tsx        # Unified chat interface
│   │   ├── components/
│   │   │   └── ui/                 # shadcn/ui components
│   │   ├── App.tsx                 # Main app component
│   │   └── main.tsx                # Entry point
│   ├── package.json                # Node dependencies
│   └── .env                        # Environment variables
│
├── SETUP_HF.md                     # NEW: HF token setup guide
├── QUICKSTART.md                   # Quick start guide
└── README.md                       # This file
```

## RAG Pipeline Flow

### Streamlit UI (FAISS-based)
1. **Upload**: Brand data uploaded via CSV/XLSX (multi-brand), PDF, or TXT (single brand)
2. **Parsing**: CSV/XLSX parsed with column mapping; PDF/TXT extracted with PyMuPDF
3. **Chunking**: Text split into 500-character chunks with 50-character overlap
4. **Embedding**: Chunks embedded using HF `intfloat/e5-small-v2` model
5. **Storage**: Embeddings stored in brand-scoped FAISS indices (`/data/vectors/<brandId>.index`)
6. **Retrieval**: When generating, top-K relevant chunks retrieved via semantic search
7. **Enhancement**: User prompt enhanced with retrieved brand context
8. **Generation**: Enhanced prompt sent to HF Inference API or local diffusers
9. **Output**: Generated content saved and returned with download link

### React UI (ChromaDB-based)
1. **Upload**: Brand metadata is uploaded via CSV/Excel file
2. **Ingestion**: Metadata is parsed and stored in ChromaDB vector database
3. **Retrieval**: When generating content, the system retrieves brand metadata by brand name
4. **Enhancement**: User prompt is enhanced with brand-specific context (tone, style, colors, etc.)
5. **Generation**: Enhanced prompt is sent to AI model (Stable Diffusion XL or ModelScope)
6. **Output**: Generated content is saved and returned to the user

## Technical Details

### Streamlit UI

**Generation Engines**:
- **Default**: Hugging Face Inference API (hosted, fast)
- **Fallback**: Local diffusers (CPU/GPU, slower but always available)

**Image Models** (via HF Inference):
- `stabilityai/sd-turbo` - 4 steps, fast generation
- `runwayml/stable-diffusion-v1-5` - Higher quality, more steps

**Video Models** (via HF Inference Endpoints):
- `stabilityai/stable-video-diffusion-img2vid` - img2vid, 12 frames
- `stabilityai/stable-video-diffusion-img2vid-xt` - Extended, 24 frames

**Vector Database** (FAISS):
- Brand-scoped indices stored in `/data/vectors/<brandId>.index`
- Metadata stored in pickle files
- Semantic search via cosine similarity (Inner Product)

**Embedding Model**:
- `intfloat/e5-small-v2` via HF Inference API
- 384-dimensional embeddings
- Normalized for cosine similarity

### React UI

**Vector Database** (ChromaDB):
- Stores brand metadata as documents with embeddings
- Enables semantic search and retrieval
- Persistent storage in `backend/data/chroma_db/`

**Image Generation** (Stable Diffusion XL):
- Model: `stabilityai/stable-diffusion-xl-base-1.0`
- Resolution: 1024x1024 (configurable)
- Inference steps: 30 (configurable)
- Guidance scale: 7.5 (configurable)

**Video Generation** (ModelScope):
- Model: `damo-vilab/text-to-video-ms-1.7b`
- Frames: 16 (configurable)
- FPS: 8
- Inference steps: 25 (configurable)

### Prompt Enhancement
The RAG pipeline enhances prompts by adding:
- Tone of voice
- Visual style
- Color palette
- Brand communications
- Target audience context

Example:
```
User prompt: "A person using skincare products"
Enhanced prompt: "A person using skincare products, warm and caring tone, 
natural and authentic style, using soft whites and blues colors, 
emphasizes real beauty and self-confidence, appealing to women of all ages, 
professional photography, high quality, detailed, 8k resolution"
```

## Performance Notes

### First-Time Setup
- Model downloads may take 10-30 minutes depending on internet speed
- Stable Diffusion XL: ~10GB
- ModelScope: ~5GB

### Generation Times
- **Image Generation**: 10-60 seconds (depending on GPU)
- **Video Generation**: 1-5 minutes (depending on GPU)
- **CPU-only**: 5-10x slower than GPU

### Hardware Requirements
- **Minimum**: 16GB RAM, CPU-only (slow)
- **Recommended**: 16GB RAM, NVIDIA GPU with 8GB+ VRAM
- **Optimal**: 32GB RAM, NVIDIA GPU with 16GB+ VRAM

## Troubleshooting

### Backend Issues

**Models not downloading**:
- Check internet connection
- Ensure sufficient disk space (~20GB free)
- Check Hugging Face access (models are public)

**Out of memory errors**:
- Reduce image resolution
- Reduce number of inference steps
- Use CPU instead of GPU (slower but uses less memory)

**ChromaDB errors**:
- Delete `backend/data/chroma_db/` and restart
- Check file permissions

### Frontend Issues

**Cannot connect to backend**:
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify `.env` file has correct API URL

**Images/videos not displaying**:
- Check browser console for errors
- Verify media files exist in `backend/data/generated_content/`
- Check file permissions

## Future Enhancements

- [ ] Support for more AI models
- [ ] Batch generation
- [ ] Advanced prompt templates
- [ ] User authentication
- [ ] Generation history
- [ ] Model fine-tuning with brand assets
- [ ] Multi-language support
- [ ] Cloud deployment guide

## License

This is a proof-of-concept project for demonstration purposes.

## Credits

- **Stable Diffusion XL** by Stability AI
- **ModelScope** by Alibaba DAMO Academy
- **ChromaDB** by Chroma
- **FastAPI** by Sebastián Ramírez
- **React** by Meta
- **shadcn/ui** by shadcn

## Support

For issues or questions, please refer to the documentation or create an issue in the repository.
