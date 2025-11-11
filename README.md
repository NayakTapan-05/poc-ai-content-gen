# AI Content Generation POC with RAG Pipeline

A proof-of-concept application for AI-powered image and video generation with Retrieval-Augmented Generation (RAG) pipeline for brand-compliant content creation.

## Overview

This POC demonstrates a complete AI content generation system that uses:
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

## Setup Instructions

### Prerequisites
- Python 3.12 or higher
- Node.js 18 or higher
- Poetry (Python package manager)
- npm or yarn
- CUDA-compatible GPU (recommended for faster generation)

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

### 1. Upload Brand Metadata (Optional)

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

### Brand Management
- `POST /api/brands/upload` - Upload brand metadata CSV/Excel
- `GET /api/brands` - List all brands
- `GET /api/brands/{brand_name}` - Get brand metadata
- `DELETE /api/brands/{brand_name}` - Delete brand

### Content Generation
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
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   ├── vector_db.py        # ChromaDB service
│   │   │   ├── image_generator.py  # Stable Diffusion XL
│   │   │   └── video_generator.py  # ModelScope
│   │   └── utils/
│   ├── data/
│   │   ├── brand_metadata/         # Uploaded brand files
│   │   ├── generated_content/      # Generated images/videos
│   │   └── chroma_db/              # ChromaDB storage
│   ├── pyproject.toml              # Python dependencies
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx     # Home page with tiles
│   │   │   └── ChatPage.tsx        # Chat interface
│   │   ├── components/
│   │   │   └── ui/                 # shadcn/ui components
│   │   ├── App.tsx                 # Main app component
│   │   └── main.tsx                # Entry point
│   ├── package.json                # Node dependencies
│   └── .env                        # Environment variables
│
└── README.md                       # This file
```

## RAG Pipeline Flow

1. **Upload**: Brand metadata is uploaded via CSV/Excel file
2. **Ingestion**: Metadata is parsed and stored in ChromaDB vector database
3. **Retrieval**: When generating content, the system retrieves brand metadata by brand name
4. **Enhancement**: User prompt is enhanced with brand-specific context (tone, style, colors, etc.)
5. **Generation**: Enhanced prompt is sent to AI model (Stable Diffusion XL or ModelScope)
6. **Output**: Generated content is saved and returned to the user

## Technical Details

### Vector Database (ChromaDB)
- Stores brand metadata as documents with embeddings
- Enables semantic search and retrieval
- Persistent storage in `backend/data/chroma_db/`

### Image Generation (Stable Diffusion XL)
- Model: `stabilityai/stable-diffusion-xl-base-1.0`
- Resolution: 1024x1024 (configurable)
- Inference steps: 30 (configurable)
- Guidance scale: 7.5 (configurable)

### Video Generation (ModelScope)
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
