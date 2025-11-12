.PHONY: setup install run-streamlit run-backend run-frontend test clean help

help:
	@echo "AI Content Generation POC - Makefile Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          - Complete setup (install dependencies)"
	@echo "  make install        - Install Python dependencies with Poetry"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run-streamlit  - Run Streamlit UI (recommended)"
	@echo "  make run-backend    - Run FastAPI backend only"
	@echo "  make run-frontend   - Run React frontend only"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean generated files and caches"
	@echo "  make help           - Show this help message"

setup: install
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Set up your Hugging Face token (see SETUP_HF.md)"
	@echo "2. Run 'make run-streamlit' to start the Streamlit UI"
	@echo "3. Open http://localhost:8501 in your browser"

install:
	@echo "📦 Installing dependencies..."
	cd backend && poetry install
	@echo "✅ Dependencies installed!"

run-streamlit:
	@echo "🚀 Starting Streamlit UI..."
	@echo "Backend API will start automatically on http://localhost:8000"
	@echo "Streamlit UI will be available at http://localhost:8501"
	@echo ""
	cd backend && poetry run streamlit run ../apps/streamlit_app.py

run-backend:
	@echo "🚀 Starting FastAPI backend..."
	@echo "API will be available at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"
	@echo ""
	cd backend && poetry run python -m fastapi dev app/main.py

run-frontend:
	@echo "🚀 Starting React frontend..."
	@echo "Frontend will be available at http://localhost:5173"
	@echo ""
	cd frontend && npm run dev

test:
	@echo "🧪 Running tests..."
	cd backend && poetry run pytest

clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf backend/data/generated_content/*
	rm -rf backend/data/vectors/*
	rm -rf backend/data/ingest/*
	rm -rf backend/data/chroma_db/*
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete!"
