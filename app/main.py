import os
import asyncio
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from loguru import logger

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.db import init_db
from app.services.ftso import FTSODataCollector

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Verifiable knowledge system for Flare's ecosystem",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error handling middleware
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# FTSO data collection task
ftso_collector = None
ftso_task = None

# Startup event handler
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    
    try:
        # Initialize databases
        db_clients = await init_db()
        logger.info("Database connections initialized")
        
        # Start FTSO data collection
        global ftso_collector, ftso_task
        ftso_collector = FTSODataCollector()
        await ftso_collector.set_redis_client(db_clients["redis"])
        
        # Start the FTSO data collection task in background
        ftso_task = asyncio.create_task(ftso_collector.start_collection_loop())
        logger.info("FTSO data collection started")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        logger.warning("Application starting in degraded mode - some features may not be available")
        # Initialize with empty clients to allow the API to start even with DB connection issues
        # Variables already declared global above
        if not ftso_collector:
            ftso_collector = FTSODataCollector()
            
        # Don't start the FTSO task if there was an error - it can be started later

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")
    
    # Cancel FTSO data collection task
    global ftso_task
    if ftso_task:
        ftso_task.cancel()
        try:
            await ftso_task
        except asyncio.CancelledError:
            logger.info("FTSO data collection task cancelled")

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "Verifiable knowledge system for Flare's ecosystem",
        "docs": "/docs",
        "api": "/api"
    }
