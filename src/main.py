"""FastAPI application entry point."""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.adapters.api.routes import conversation, health
from src.adapters.api.schemas.responses import ErrorResponse
from src.adapters.dependency_injection.container import cleanup_redis_connections

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Debate Chatbot API",
    description="A chatbot that holds debates and attempts to convince users of its views",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(conversation.router)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Debate Chatbot API...")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Debate Chatbot API...")
    await cleanup_redis_connections()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc)
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)