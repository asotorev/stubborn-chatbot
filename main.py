"""
Root entry point for the Stubborn Chatbot API.
This imports and runs the FastAPI application from the src package.
"""

from src.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)