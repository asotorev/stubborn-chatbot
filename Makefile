.PHONY: help install test run down clean build logs

# Default target - shows help
help:
	@echo "Stubborn Chatbot API - Available Commands:"
	@echo ""
	@echo "  make install    - Install all requirements to run the service"
	@echo "  make test       - Run tests"
	@echo "  make build      - Build Docker images"
	@echo "  make run        - Run the service and all related services in Docker"
	@echo "  make logs       - View service logs"
	@echo "  make down       - Teardown of all running services"
	@echo "  make clean      - Teardown and removal of all containers"
	@echo "  make help       - Show this help message"
	@echo ""

# Install dependencies
install:
	@echo "Checking for required tools..."
	@command -v docker >/dev/null 2>&1 || { echo "ERROR: Docker is required but not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 || { echo "ERROR: Docker Compose is required but not installed. Please install Docker Compose from https://docs.docker.com/compose/install/"; exit 1; }
	@echo "Building Docker images..."
	@make build
	@echo "Installation complete. Use 'make run' to start the service."

# Run tests
test:
	@echo "Running tests..."
	@docker-compose run --rm api python -m pytest tests/ -v

# Build Docker images
build:
	@echo "Building Docker images..."
	@docker-compose build

# Run services
run:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "API available at: http://localhost:8000"
	@echo "API documentation: http://localhost:8000/docs"
	@echo "Use 'make logs' to view logs, 'make down' to stop"

# View logs
logs:
	@echo "Viewing service logs (Ctrl+C to exit)..."
	@docker-compose logs -f

# Stop services
down:
	@echo "Stopping services..."
	@docker-compose down

# Clean up everything
clean:
	@echo "Cleaning up containers, networks, and images..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f --volumes

# Development helpers
dev-install:
	@echo "Setting up local development environment..."
	@if [ "$(PYTHON)" = "python-not-found" ]; then \
		echo "ERROR: Python is required but not found."; \
		echo "Please install Python 3.8+ from https://www.python.org/downloads/"; \
		exit 1; \
	fi
	@echo "Creating virtual environment at ~/venvs/stubborn-chatbot..."
	@$(PYTHON) -m venv ~/venvs/stubborn-chatbot
	@echo "Installing dependencies..."
	@~/venvs/stubborn-chatbot/bin/pip install --upgrade pip
	@~/venvs/stubborn-chatbot/bin/pip install -r requirements.txt
	@echo "Virtual environment ready! Activate with: source ~/venvs/stubborn-chatbot/bin/activate"

dev-run:
	@echo "Starting development server..."
	@$(PYTHON) main.py

# Auto-detect Python command
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "python-not-found")
