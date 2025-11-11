# AI Content Generation POC

A local-first proof-of-concept for AI-powered content generation using **100% open-source models**. Generate brand-compliant images and videos with RAG-enhanced prompts, multi-session chat, and intelligent content routing.

## Features

- **🎨 Real Image Generation**: Stable Diffusion Turbo (GPU) or ONNX (CPU fallback)
- **🎬 Real Video Generation**: Stable Video Diffusion for both GPU and CPU
- **🧠 RAG Pipeline**: FAISS + sentence-transformers for brand knowledge retrieval
- **💬 Multi-Session Chat**: SQLite-backed persistent chat history
- **🎯 Template-First Generation**: Pre-defined templates for consistent content
- **🛡️ Safety Checks**: Detoxify (text) + NudeNet (image) content moderation
- **🤖 Intelligent Agent**: Auto-detects intent (Q&A vs image vs video generation)
- **⚡ GPU/CPU Auto-Detection**: Automatically uses best available hardware

## Quick Start

### Prerequisites

- Python 3.12+ with Poetry
- Node.js 18+ with npm
- (Optional) CUDA-capable GPU for faster generation

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd poc-ai-content-gen

# Install all dependencies (backend + frontend)
make setup
```

### Running Locally

```bash
# Start both API and web servers
make dev

# Or start them separately:
make api  # Backend at http://localhost:8000
make web  # Frontend at http://localhost:5173
```

The application will automatically:
- Initialize the SQLite database
- Create necessary data directories
- Detect GPU availability and configure models accordingly

### First Steps

1. **Upload Brand Documents** (optional):
   - Navigate to the landing page
   - Upload brand guidelines (PDF, DOCX, TXT, CSV)
   - Documents are processed and indexed for RAG retrieval

2. **Start Chatting**:
   - Go to the Chat page
   - Select a brand (if uploaded) or use without brand context
   - Describe what you want to create
   - The agent will automatically detect if you want an image or video

3. **Generate Content**:
   - Images: "Create a product photo of a coffee mug"
   - Videos: "Generate a video of waves on a beach"
   - Q&A: "What is our brand's tone of voice?"

## Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── deps.py              # Dependency injection
│   ├── adapters/            # External service adapters
│   │   ├── embeddings_local.py      # sentence-transformers
│   │   ├── vector_faiss.py          # FAISS vector store
│   │   ├── image_provider_local.py  # SD-Turbo/ONNX
│   │   ├── video_provider_local.py  # Stable Video Diffusion
│   │   ├── caption_local.py         # BLIP captioning
│   │   └── safety_local.py          # Detoxify + NudeNet
│   ├── services/            # Business logic
│   │   ├── rag/             # RAG pipeline
│   │   ├── generation/      # Content generation
│   │   ├── agent/           # Intent detection & routing
│   │   └── safety.py        # Safety checks
│   ├── routers/             # API endpoints
│   │   ├── session.py       # Session management
│   │   ├── history.py       # Chat history
│   │   ├── templates.py     # Content templates
│   │   ├── rag.py           # Document ingestion
│   │   ├── generate.py      # Direct generation
│   │   └── agent.py         # Intelligent chat
│   └── db/                  # Database
│       └── database.py      # SQLite operations
└── tests/
    └── test_acceptance.py   # Acceptance tests
```

### Frontend (React + TypeScript)

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LandingPage.tsx  # Home & brand upload
│   │   └── ChatPage.tsx     # Multi-session chat UI
│   └── components/          # Reusable UI components
```

### Data Directory

```
data/
├── vectors/              # FAISS indices (per brand)
├── ingest/              # Uploaded documents (per brand)
├── generated_content/   # Generated images & videos
└── app.db              # SQLite database
```

## Models Used

| Component | GPU Model | CPU Fallback | Purpose |
|-----------|-----------|--------------|---------|
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Same | Text embeddings for RAG |
| **Vector DB** | FAISS (CPU/GPU) | FAISS (CPU) | Similarity search |
| **Image Gen** | stabilityai/sd-turbo | SD ONNX (256x256) | Image generation |
| **Video Gen** | stabilityai/stable-video-diffusion-img2vid-xt | Same (reduced settings) | Video generation |
| **Caption** | Salesforce/blip-image-captioning-base | Same | Image validation |
| **Text Safety** | Detoxify | Same | Toxicity detection |
| **Image Safety** | NudeNet | Same | NSFW detection |

## Configuration

All settings are configurable via environment variables. Copy `.env.example` to `.env` and customize:

```bash
# Core Settings
API_PORT=8000
WEB_PORT=3000
DATA_DIR=./data
USE_GPU_IF_AVAILABLE=true

# Model Selection
IMAGE_MODEL=sd-turbo        # sd-turbo, sd15, or onnx
VIDEO_MODEL=svd-xt          # svd-xt
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
CAPTION_MODEL=blip-base

# Generation Settings
IMAGE_SIZE=256              # Image dimensions
IMAGE_STEPS=8               # Inference steps
VIDEO_FRAMES=8              # Video frames
VIDEO_STEPS=8               # Video inference steps
VIDEO_FPS=8                 # Frames per second

# RAG Settings
RAG_CHUNK_SIZE=900          # Text chunk size
RAG_CHUNK_OVERLAP=120       # Chunk overlap
RAG_TOP_K=5                 # Top results to retrieve

# Safety
ENABLE_SAFETY_CHECKS=true
ENABLE_WATERMARK=true
```

## API Endpoints

### Sessions
- `POST /api/sessions` - Create new chat session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session

### Chat History
- `GET /api/history/{session_id}` - Get session messages

### RAG
- `POST /api/rag/ingest` - Ingest documents for a brand
- `GET /api/rag/brands` - List all brands
- `POST /api/rag/retrieve` - Retrieve relevant context
- `DELETE /api/rag/brands/{brand_id}` - Delete brand data

### Templates
- `GET /api/templates` - List all templates
- `GET /api/templates/{id}` - Get template details
- `POST /api/templates/fill` - Fill template with values

### Generation
- `POST /api/generate/image` - Generate image directly
- `POST /api/generate/video` - Generate video directly

### Agent
- `POST /api/agent/chat` - Intelligent chat endpoint (auto-routes)

## Testing

```bash
# Run acceptance tests
make test

# Or manually
cd backend
poetry run pytest tests/test_acceptance.py -v
```

Tests verify:
1. Database initialization and multi-session chat
2. RAG pipeline with FAISS and embeddings
3. Safety checks (Detoxify + NudeNet)
4. Template system
5. End-to-end generation flow

## Performance Expectations

### GPU Mode (CUDA)
- **Image Generation**: ~2-5 seconds (SD-Turbo), ~10-15 seconds (SD1.5)
- **Video Generation**: ~30-60 seconds (25 frames, 256p)
- **RAG Retrieval**: <1 second

### CPU Mode
- **Image Generation**: ~30-60 seconds (ONNX, 256x256, 8 steps)
- **Video Generation**: ~5-10 minutes (8 frames, 256p, 8 steps)
- **RAG Retrieval**: <2 seconds

CPU mode uses reduced settings but produces **real model outputs** (no mocks).

## Docker (Optional)

```bash
# Start with docker-compose
make up

# Stop services
make down
```

Docker is **optional**. The application is designed to run locally with Python venv + Node.

## Troubleshooting

### Out of Memory (GPU)
- Reduce `IMAGE_SIZE` to 256 or 128
- Reduce `VIDEO_FRAMES` to 8
- Set `IMAGE_MODEL=onnx` to force CPU mode

### Slow Generation (CPU)
- This is expected on CPU
- Reduce `IMAGE_STEPS` to 6-8
- Reduce `VIDEO_FRAMES` to 8
- Increase `TEST_TIMEOUT_SEC` for tests

### Models Not Downloading
- Ensure internet connection for first run
- Models are cached in `~/.cache/huggingface/`
- Check disk space (models are ~5-10GB total)

### FAISS Index Errors
- Delete `data/vectors/` and re-ingest documents
- Ensure consistent embedding model

## Development

```bash
# Clean generated files
make clean

# Seed database
make seed

# Ingest sample documents
make ingest
```

## Architecture Decisions

### Why FAISS over ChromaDB?
- Lighter weight, no server required
- Better performance for small-to-medium datasets
- Easier to deploy and maintain

### Why SQLite over PostgreSQL?
- Local-first design
- No external dependencies
- Sufficient for POC scale
- Easy backup and migration

### Why Sentence-Transformers?
- Fast, efficient embeddings
- Good quality for RAG use cases
- Works well on CPU

### Why SD-Turbo?
- 4x faster than SD1.5
- Good quality for POC
- Lower VRAM requirements

## License

This is a proof-of-concept project. All models used are open-source with their respective licenses.

## Contributing

This is a POC project. For production use, consider:
- Adding authentication and authorization
- Implementing rate limiting
- Adding monitoring and logging
- Using a production database
- Implementing proper error handling
- Adding comprehensive test coverage
- Optimizing model loading and caching

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Diffusers](https://huggingface.co/docs/diffusers/)
- [Sentence-Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
