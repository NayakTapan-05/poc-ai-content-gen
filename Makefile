.PHONY: setup install run-streamlit run-backend test clean help

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
	@echo "2. Run 'make run-backend' in one terminal"
	@echo "3. Run 'make run-streamlit' in another terminal"
	@echo "4. Open http://localhost:8501 in your browser"

install:
	@echo "📦 Installing dependencies..."
	cd backend && poetry install
	@echo "✅ Dependencies installed!"

run-streamlit:
	@echo "🚀 Starting Streamlit UI..."
	@echo "Streamlit UI will be available at http://localhost:8501"
	@echo ""
	@echo "⚠️  Make sure backend is running first (make run-backend)"
	@echo ""
	cd backend && poetry run streamlit run ../apps/streamlit_app.py

run-backend:
	@echo "🚀 Starting FastAPI backend..."
	@echo "API will be available at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"
	@echo ""
	cd backend && poetry run python -m fastapi dev app/main.py

test:
	@echo "🧪 Running tests..."
	cd backend && poetry run pytest

clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf backend/data/generated_content/*
	rm -rf backend/data/vectors/*
	rm -rf backend/data/ingest/*
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete!"
