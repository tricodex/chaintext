"""
Run script for ChainContext API server
"""
import os
import uvicorn
from app.core.config import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main entry point for the application"""
    print(f"Starting {settings.APP_NAME} v{settings.VERSION} API server")
    
    # Check for required environment variables
    if not settings.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not set. Gemini functionality will not work.")
    
    # Start the API server
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
