# Stubborn Chatbot API

A persuasive chatbot that debates and stands its ground on controversial topics.

## Quick Start

1. Copy environment variables:

   ```bash
   cp env.example .env
   ```

2. Add your OpenAI API key to `.env`

3. Set up virtual environment and install dependencies:

   ```bash
   # Using Docker (recommended)
   make install
   make run

   # Or for local development
   make dev-install
   source ~/venvs/stubborn-chatbot/bin/activate
   ```

4. Run the application:
   ```bash
   # Using Docker
   make run

   # Or locally (with virtual environment activated)
   python main.py
   ```

## API Endpoints

- `GET /health` - Health check endpoint

More endpoints will be added as development progresses.
