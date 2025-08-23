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
	@echo "  make chat       - Start interactive chat CLI in Docker"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Advanced/Development Commands:"
	@echo "  make dev-install - Set up local Python environment for development"
	@echo "  make dev-run     - Run API server locally (without Docker)"
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

# Interactive chat CLI
chat:
	@echo "Starting interactive chat CLI in Docker..."
	@echo "Note: Make sure your .env file contains OPENAI_API_KEY for full functionality"
	@docker-compose --profile chat run --rm chat || { \
		echo ""; \
		echo "Docker not available. Trying local Python fallback..."; \
		echo "Note: This requires Python dependencies to be installed locally."; \
		$(PYTHON) chat.py 2>/dev/null || { \
			echo ""; \
			echo "Local Python fallback failed."; \
			echo "Either:"; \
			echo "  1. Start Docker and try again, OR"; \
			echo "  2. Run 'make dev-install' first for local Python setup"; \
			exit 1; \
		}; \
	}

# Auto-detect Python command
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "python-not-found")
