.PHONY: help setup api web dev seed ingest test clean up down

help:
	@echo "AI Content Generation POC - Makefile Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup    - Install all dependencies (backend + frontend)"
	@echo ""
	@echo "Development:"
	@echo "  make api      - Start backend API server"
	@echo "  make web      - Start frontend development server"
	@echo "  make dev      - Start both API and web in parallel"
	@echo ""
	@echo "Data & Testing:"
	@echo "  make seed     - Seed database with sample data"
	@echo "  make ingest   - Ingest sample brand documents"
	@echo "  make test     - Run all tests"
	@echo ""
	@echo "Docker (Optional):"
	@echo "  make up       - Start services with docker-compose"
	@echo "  make down     - Stop docker-compose services"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean    - Clean generated files and caches"

setup:
	@echo "Installing backend dependencies..."
	cd backend && poetry install
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Setup complete!"

api:
	@echo "Starting backend API server..."
	cd backend && poetry run fastapi dev app/main.py

web:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

dev:
	@echo "Starting both API and web servers..."
	@echo "API will be at http://localhost:8000"
	@echo "Web will be at http://localhost:5173"
	@$(MAKE) -j2 api web

seed:
	@echo "Seeding database with sample data..."
	cd backend && poetry run python -c "import asyncio; from app.deps import get_db; from app.db.database import Database; asyncio.run(get_db())"
	@echo "Database seeded!"

ingest:
	@echo "Ingesting sample brand documents..."
	@echo "Use: curl -X POST 'http://localhost:8000/api/rag/ingest?brand_id=sample' -F 'files=@path/to/file.pdf'"
	@echo "Or use the frontend UI to upload documents"

test:
	@echo "Running tests..."
	cd backend && poetry run pytest tests/ -v

clean:
	@echo "Cleaning generated files and caches..."
	rm -rf backend/data/generated_content/*
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete
	@echo "Clean complete!"

up:
	@echo "Starting services with docker-compose..."
	docker-compose up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "Web: http://localhost:3000"

down:
	@echo "Stopping docker-compose services..."
	docker-compose down
	@echo "Services stopped!"
