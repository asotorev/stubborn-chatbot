# Stubborn Chatbot API

A debate chatbot that holds conversations and attempts to convince users of its views, regardless of how controversial the topic. The bot maintains its stance throughout the conversation and provides persuasive arguments.

## Features

- **Intelligent Debate Bot** - Powered by OpenAI GPT models
- **Conversation Management** - Maintains context across multiple messages
- **Stance Consistency** - Bot maintains its assigned position throughout the debate
- **Topic Generation** - Automatically selects debate topics and takes a stance
- **Persistent Storage** - Redis-backed conversation storage with memory fallback
- **Docker Ready** - Complete containerized deployment
- **Comprehensive Testing** - Unit and integration tests included

## API Interface

The API follows the challenge specification:

### Request Format

```json
{
    "conversation_id": "text" | null,
    "message": "text"
}
```

### Response Format

```json
{
  "conversation_id": "text",
  "messages": [
    {
      "role": "user",
      "message": "text"
    },
    {
      "role": "bot",
      "message": "text"
    }
  ]
}
```

### Starting a Conversation

- Send a message with `conversation_id: null` to start a new debate
- The first message defines the topic and the bot automatically takes a stance
- The bot will respond with its position and begin the debate

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### 1. Environment Setup

```bash
# Copy environment configuration
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

**Note**: When using Docker (recommended), Redis configuration is automatically set to use the containerized Redis service. For local development, the default configuration points to `localhost:6379`.

### 2. Run with Docker (Recommended)

```bash
# Install dependencies and start services
make install
make run

# The API will be available at http://localhost:8000
```

### 3. Test the API

```bash
# Start a new conversation
curl -X POST http://localhost:8000/conversation \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": null, "message": "I think climate change is real"}'

# Continue the conversation
curl -X POST http://localhost:8000/conversation \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "returned-id", "message": "But what about natural cycles?"}'
```

### 4. Interactive CLI Mode

```bash
# Run the interactive chat interface
make chat

# Or with Docker Compose
docker-compose --profile chat up chat
```

## Environment Variables

| Variable         | Description                          | Default                  | Required |
| ---------------- | ------------------------------------ | ------------------------ | -------- |
| `OPENAI_API_KEY` | Your OpenAI API key                  | -                        | Yes      |
| `STORAGE_TYPE`   | Storage backend: "memory" or "redis" | "memory"                 | No       |
| `REDIS_URL`      | Redis connection URL                 | "redis://localhost:6379" | No       |
| `PORT`           | API server port                      | 8000                     | No       |

## Storage Options

### Memory Storage (Default)

- Fast in-memory conversation storage
- Data lost on application restart
- Perfect for development and testing

### Redis Storage (Production)

- Persistent conversation storage
- Data survives application restarts
- Automatic fallback to memory if Redis unavailable

To enable Redis for local development:

```bash
# Set in .env file
STORAGE_TYPE=redis
# REDIS_URL=redis://localhost:6379  # Default, already configured
```

**Docker users**: Redis is automatically enabled when using `make run`. No additional configuration needed.

## Makefile Commands

| Command        | Description                       |
| -------------- | --------------------------------- |
| `make`         | Show all available commands       |
| `make install` | Install dependencies and setup    |
| `make test`    | Run all tests                     |
| `make run`     | Start the API server with Docker  |
| `make down`    | Stop all running services         |
| `make clean`   | Remove all containers and cleanup |
| `make chat`    | Start interactive CLI mode        |

## API Endpoints

| Endpoint        | Method | Description                      |
| --------------- | ------ | -------------------------------- |
| `/health`       | GET    | Health check and system status   |
| `/conversation` | POST   | Start or continue a conversation |
| `/docs`         | GET    | Interactive API documentation    |

## Architecture

The application follows Clean Architecture principles:

- **Domain Layer** - Core entities and business rules
- **Use Cases** - Application business logic
- **Interface Adapters** - API routes and schemas
- **Infrastructure** - External services (OpenAI, Redis)

## Testing

```bash
# Run all tests
make test

# Run specific test types
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Run Redis integration tests (requires Docker)
python -m pytest tests/integration/test_redis_integration.py -v
```

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

### Project Structure

```
├── src/
│   ├── core/                 # Domain entities and use cases
│   ├── adapters/            # API routes and dependency injection
│   └── infrastructure/      # External services and repositories
├── tests/                   # Unit and integration tests
├── docker-compose.yml       # Container orchestration
├── Dockerfile              # Container definition
└── Makefile                # Development commands
```

## Deployment

The application is designed for easy deployment:

1. **Environment Variables** - Configure via `.env` file
2. **Docker Support** - Complete containerization
3. **Health Checks** - Built-in monitoring endpoints
4. **Graceful Fallback** - Continues working if Redis unavailable
