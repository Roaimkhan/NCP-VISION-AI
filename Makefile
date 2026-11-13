.PHONY: setup warm-ocr seed dev-backend dev-frontend test

setup:
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install && npm install recharts

warm-ocr:
	@echo "OCR warmup not configured yet"

seed:
	@echo "Seed not configured yet"

dev-backend:
	cd backend && ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev -- --hostname 0.0.0.0 --port 3000

test:
	./.venv/bin/pytest -q
