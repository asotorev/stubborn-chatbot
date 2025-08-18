"""
Main entry point for the Stubborn Chatbot API.

This module initializes the FastAPI application.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Stubborn Chatbot API",
        description="A persuasive chatbot that debates and stands its ground",
        version="1.0.0"
    )
    
    # TODO: Add routers and middleware in future commits
    
    return app


# Application instance
app = create_app()


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "message": "Stubborn Chatbot API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
