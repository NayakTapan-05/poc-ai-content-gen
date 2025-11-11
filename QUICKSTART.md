# Quick Start Guide

## Prerequisites
- Python 3.12+
- Node.js 18+
- Poetry (install: `curl -sSL https://install.python-poetry.org | python3 -`)
- Git

## 1. Clone or Download Repository

If you're setting this up from the tarball:
```bash
tar -xzf poc-ai-content-gen.tar.gz
cd poc-ai-content-gen
```

## 2. Backend Setup (5 minutes)

```bash
cd backend

# Install dependencies (this will take a few minutes)
poetry install

# Start the backend server
poetry run fastapi dev app/main.py
```

The backend will start on `http://localhost:8000`

**Note**: The first time you generate content, AI models will download automatically (~15GB total). This is a one-time download.

## 3. Frontend Setup (2 minutes)

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

## 4. Upload Brand Metadata (Optional)

You can upload brand metadata CSV files to enable RAG-enhanced generation:

```bash
curl -X POST "http://localhost:8000/api/brands/upload?brand_name=YourBrand" \
  -F "file=@your_brand_metadata.csv"
```

CSV format (2 columns):
```csv
brand_key,brand_value
tone_of_voice,Warm and caring
visual_style,Natural and authentic
color_palette,Soft blues and whites
```

A sample template is provided at `backend/data/brand_metadata/sample_brand_template.csv`

## 5. Start Creating!

1. Open `http://localhost:5173` in your browser
2. Click "Image Generation" or "Video Generation"
3. (Optional) Select a brand if you uploaded metadata
4. Type your prompt and press Enter
5. Wait for generation (10-60 seconds for images, 1-5 minutes for videos)
6. Download your generated content!

## Example Prompts

**Without brand context**:
- "A beautiful sunset over mountains"
- "A person jogging in a park"

**With brand context** (e.g., Dove):
- "Make me a campaign image for Dove brand"
- "Create a video showing real beauty and confidence"

## Troubleshooting

**Backend won't start**:
- Check Python version: `python --version` (should be 3.12+)
- Reinstall dependencies: `poetry install`

**Frontend won't start**:
- Check Node version: `node --version` (should be 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**Generation is slow**:
- First generation downloads models (~15GB)
- CPU-only generation is 5-10x slower than GPU
- Consider using a machine with NVIDIA GPU

**Out of memory**:
- Close other applications
- Reduce image resolution in the API request
- Use fewer inference steps

## API Documentation

Interactive API docs available at: `http://localhost:8000/docs`

## Next Steps

- Upload your brand metadata CSV files
- Customize the frontend branding
- Adjust generation parameters in the API
- Deploy to production (see README.md)

Enjoy creating AI-powered content! 🎨🎬
