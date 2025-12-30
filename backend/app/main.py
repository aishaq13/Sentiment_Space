"""
Sentiment Space Backend
On-device AI assistant for thought summarization and sentiment analysis.

Privacy-first architecture:
- Runs Llama 3 locally (CPU, quantized)
- No cloud calls by default
- Data stored locally in SQLite
- Optional S3 export with explicit user consent
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import after logging config
from app.api.routes import router as api_router
from app.utils.config import Config

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

# Create FastAPI app
app = FastAPI(
    title="Sentiment Space API",
    description="Privacy-first, on-device sentiment analysis and thought summarization",
    version="0.1.0",
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8100", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and models on startup."""
    logger.info("Sentiment Space backend starting...")
    logger.info(f"Environment: {Config.FASTAPI_ENV}")
    logger.info(f"Database: {Config.DB_PATH}")
    logger.info(f"LLM Model: {Config.LLM_MODEL_NAME}")
    logger.info(f"Device: {Config.LLM_DEVICE}")
    logger.info(f"S3 Export: {'Enabled' if Config.S3_ENABLED else 'Disabled'}")

    # Ensure data directory exists
    db_dir = os.path.dirname(Config.DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Created data directory: {db_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Sentiment Space backend shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.FASTAPI_HOST,
        port=Config.FASTAPI_PORT,
        reload=Config.FASTAPI_DEBUG,
    )
