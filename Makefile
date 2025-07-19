BACKEND_PATH=server
FRONTEND_PATH=client

start-backend:
	@echo "Starting FastAPI backend..."
	cd $(BACKEND_PATH) && uvicorn src.main:app --reload

start-frontend:
	@echo "Starting Next.js frontend..."
	cd $(FRONTEND_PATH) && npm run dev

start:
	@echo "Starting both backend and frontend..."
	make start-backend & make start-frontend

stop:
	@echo "Stopping all backend and frontend processes..."
	lsof -ti:8000 | xargs kill -9 || true
	lsof -ti:3000 | xargs kill -9 || true