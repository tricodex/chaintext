"""
Development script for ChainContext API server with hot reloading
"""
import os
import uvicorn
from app.core.config import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main entry point for the development server"""
    print(f"Starting {settings.APP_NAME} v{settings.VERSION} Development Server")
    
    # Check for required environment variables
    if not settings.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not set. Gemini functionality will not work.")
    
    # Start the API server with hot reloading
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    main()
