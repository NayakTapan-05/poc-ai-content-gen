# AI Content Generation POC with RAG Pipeline

A proof-of-concept application for AI-powered image and video generation with Retrieval-Augmented Generation (RAG) pipeline for brand-compliant content creation.

## Overview

This POC demonstrates a complete AI content generation system with **Streamlit UI**:

### 🎨 Features
- **Hugging Face Inference API** for fast, cloud-based generation
- **FAISS** vector database for brand metadata
- **Floating Action Button (FAB)** with template picker
- **Chat interface** with multi-turn conversations
- **Brand data upload** (CSV/XLSX/PDF/TXT)
- **Runtime model selection** (2 image + 2 video models)
- **FastAPI** backend with RESTful API

## Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **FAISS** - Vector database for brand metadata storage
- **Hugging Face Inference API** - Cloud-based image and video generation
- **RAG Pipeline** - Retrieves brand metadata and enhances prompts

### Frontend
- **Streamlit** - Python-based web UI framework
- **Interactive chat interface** - Multi-turn conversations
- **Template picker** - Guided content generation
- **Brand data management** - Upload and manage brand knowledge

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

## Quick Start

### Prerequisites
- Python 3.12 or higher
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
cd backend
poetry install
```

4. **Run the backend** (Terminal 1):
```bash
make run-backend
# Or: cd backend && poetry run python -m fastapi dev app/main.py
```

5. **Run the Streamlit app** (Terminal 2):
```bash
make run-streamlit
# Or: cd backend && poetry run streamlit run ../apps/streamlit_app.py
```

6. **Open your browser**: http://localhost:8501

## Full Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your HF_TOKEN
```

4. Start the backend server:
```bash
poetry run python -m fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`

### Streamlit UI Setup

1. Make sure the backend is running (see above)

2. Start the Streamlit app:
```bash
cd backend
poetry run streamlit run ../apps/streamlit_app.py
```

The Streamlit UI will be available at `http://localhost:8501`

## Usage

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

## API Endpoints

### Core Endpoints
- `GET /healthz` - Health check endpoint
- `GET /api/models` - Get available models (2 image + 2 video)
- `POST /api/generate` - Unified generation endpoint (image/video)
- `GET /api/templates` - Get template catalog
- `GET /api/templates/{id}` - Get specific template
- `POST /api/brand/upload` - Upload brand data (CSV/XLSX/PDF/TXT)
- `GET /api/brand/list` - List all brands (FAISS)
- `GET /api/rag/stats?brandId=` - Get per-brand RAG statistics

### API Documentation
Interactive API documentation is available at `http://localhost:8000/docs`

## Project Structure

```
poc-ai-content-gen/
├── apps/
│   └── streamlit_app.py            # Streamlit UI
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   ├── hf_generator.py     # HF Inference API
│   │   │   ├── faiss_rag.py        # FAISS RAG service
│   │   │   └── brand_uploader.py   # Brand data ingestion
│   │   └── utils/
│   ├── data/
│   │   ├── templates/              # Template catalog
│   │   ├── vectors/                # FAISS indices
│   │   ├── ingest/                 # Ingested brand data
│   │   └── generated_content/      # Generated images/videos
│   ├── .env.example                # Environment template
│   ├── pyproject.toml              # Python dependencies
│   └── README.md
│
├── SETUP_HF.md                     # HF token setup guide
├── QUICKSTART.md                   # Quick start guide
├── Makefile                        # Build commands
└── README.md                       # This file
```

## RAG Pipeline Flow

1. **Upload**: Brand data uploaded via CSV/XLSX (multi-brand), PDF, or TXT (single brand)
2. **Parsing**: CSV/XLSX parsed with column mapping; PDF/TXT extracted with PyMuPDF
3. **Chunking**: Text split into 500-character chunks with 50-character overlap
4. **Embedding**: Chunks embedded using HF `intfloat/e5-small-v2` model
5. **Storage**: Embeddings stored in brand-scoped FAISS indices (`/data/vectors/<brandId>.index`)
6. **Retrieval**: When generating, top-K relevant chunks retrieved via semantic search
7. **Enhancement**: User prompt enhanced with retrieved brand context
8. **Generation**: Enhanced prompt sent to HF Inference API
9. **Output**: Generated content saved and returned with download link

## Technical Details

**Generation Engine**:
- Hugging Face Inference API (hosted, fast)

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

### Generation Times (via HF Inference API)
- **Image Generation**: 5-15 seconds
- **Video Generation**: 30-90 seconds (requires HF Inference Endpoint)

### Hardware Requirements
- **Minimum**: 8GB RAM, CPU-only
- **Recommended**: 16GB RAM for faster local operations

## Troubleshooting

### Backend Issues

**HF services not available**:
- Check that HF_TOKEN is set in `backend/.env`
- Verify token is valid at https://huggingface.co/settings/tokens
- Restart backend after setting token

**Generation fails**:
- Check HF_TOKEN is valid
- For video generation, ensure HF Inference Endpoints are configured
- Check backend logs for detailed error messages

**FAISS errors**:
- Delete `backend/data/vectors/` and re-upload brand data
- Check file permissions

### Streamlit Issues

**Cannot connect to backend**:
- Ensure backend is running on port 8000
- Check that both backend and Streamlit are running
- Verify `.env` file exists in `backend/` directory

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

- **Stable Diffusion** by Stability AI
- **Hugging Face** for Inference API and models
- **FAISS** by Meta AI Research
- **FastAPI** by Sebastián Ramírez
- **Streamlit** by Snowflake

## Support

For issues or questions, please refer to the documentation or create an issue in the repository.
