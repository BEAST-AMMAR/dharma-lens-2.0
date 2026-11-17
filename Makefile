# VidhiChakshu (विधि-चक्षु) - Build & Operations Automation Makefile

.PHONY: help build build-dev up down restart logs health clean test

# Default target
help:
	@echo "VidhiChakshu Management Commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start core services"
	@echo "  make up-extended - Start all services (Database, Redis, Grafana)"
	@echo "  make down        - Stop all containers"
	@echo "  make logs        - Follow service logs"
	@echo "  make health      - Check service health status"
	@echo "  make clean       - Remove unused Docker resources"
	@echo "  make test        - Run Python & Node test suites"

# Build production images
build:
	@echo "Building VidhiChakshu production containers..."
	docker-compose build --no-cache

# Build development images
build-dev:
	@echo "Building VidhiChakshu development containers..."
	docker-compose -f docker-compose.extended.yml build

# Start core services (Frontend, Node API Gateway, Python ML Engine)
up:
	@echo "Starting VidhiChakshu core stack..."
	docker-compose up -d

# Start full ecosystem (with DB, Caching, Prometheus, Grafana)
up-extended:
	@echo "Starting VidhiChakshu extended stack..."
	docker-compose -f docker-compose.extended.yml up -d

# Stop services
down:
	@echo "Stopping VidhiChakshu containers..."
	docker-compose down

# Restart core services
restart:
	@echo "Restarting VidhiChakshu services..."
	docker-compose restart

# View aggregated logs
logs:
	docker-compose logs -f --tail=100

# Health check
health:
	@echo "Checking VidhiChakshu services status..."
	@curl -s http://localhost/index.html > /dev/null && echo "[OK] Frontend (8080)" || echo "[FAIL] Frontend"
	@curl -s http://localhost:3000/health | grep -q "ok" && echo "[OK] API Gateway (3000)" || echo "[FAIL] API Gateway"
	@curl -s http://localhost:8000/health | grep -q "ok" && echo "[OK] ML Engine (8000)" || echo "[FAIL] ML Engine"

# Run tests
test:
	@echo "Running VidhiChakshu Python and Node tests..."
	python python_backend/tests/test_pipeline.py
	cd node_backend && npm test

# Cleanup
clean:
	docker system prune -f
