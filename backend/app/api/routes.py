"""
API routes for Sentiment Space backend.
Exposes endpoints for analysis, storage, and export.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ThoughtRequest(BaseModel):
    """Request model for thought analysis."""

    raw_text: str


class ThoughtResponse(BaseModel):
    """Response model for analyzed thought."""

    id: int
    raw_text: str
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    created_at: str


class EntriesResponse(BaseModel):
    """Response model for list of thoughts."""

    total: int
    entries: List[ThoughtResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status and version information
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
    }


@router.post("/analyze", response_model=ThoughtResponse)
async def analyze_thought(request: ThoughtRequest):
    """
    Analyze a thought for sentiment and generate summary.

    This endpoint:
    1. Runs local Llama 3 for summarization + sentiment
    2. Stores results in local SQLite
    3. Returns immediately (no cloud calls, ~2-5s for CPU inference)

    Args:
        request: ThoughtRequest with raw_text

    Returns:
        Analyzed thought with summary and sentiment
    """
    from app.db.database import Database
    from app.utils.config import Config
    from app.llm.llama_loader import LlamaLoader
    from app.llm.langchain_pipeline import SentimentAnalysisPipeline

    # Initialize components
    db = Database(Config.DB_PATH)
    llama_loader = LlamaLoader(
        model_name=Config.LLM_MODEL_NAME,
        quantization=Config.LLM_QUANTIZATION,
        device=Config.LLM_DEVICE,
    )

    # Load model if not already loaded
    if not llama_loader.is_available():
        llama_loader.load()

    # Run analysis pipeline
    pipeline = SentimentAnalysisPipeline(llama_loader)
    analysis = pipeline.analyze(request.raw_text)

    # Store in database
    thought_id = db.insert_thought(
        raw_text=request.raw_text,
        summary=analysis["summary"],
        sentiment=analysis["sentiment"],
        confidence=analysis["confidence"],
    )

    # Return result
    thought = db.get_thought(thought_id)

    return ThoughtResponse(
        id=thought["id"],
        raw_text=thought["raw_text"],
        summary=thought["summary"],
        sentiment=thought["sentiment"],
        confidence=thought["confidence"],
        created_at=thought["created_at"],
    )


@router.get("/entries", response_model=EntriesResponse)
async def get_entries(limit: int = 100, offset: int = 0):
    """
    Retrieve all stored thoughts.

    Args:
        limit: Maximum number of entries
        offset: Number of entries to skip

    Returns:
        List of stored thoughts with metadata
    """
    from app.db.database import Database
    from app.utils.config import Config

    db = Database(Config.DB_PATH)
    entries = db.get_all_thoughts(limit=limit, offset=offset)
    stats = db.get_stats()

    return EntriesResponse(
        total=stats["total"],
        entries=[
            ThoughtResponse(
                id=entry["id"],
                raw_text=entry["raw_text"],
                summary=entry["summary"],
                sentiment=entry["sentiment"],
                confidence=entry["confidence"],
                created_at=entry["created_at"],
            )
            for entry in entries
        ],
    )


@router.post("/export")
async def export_to_s3(thought_ids: Optional[List[int]] = None):
    """
    Export thoughts to AWS S3 (optional feature).

    This is COMPLETELY OPTIONAL and requires:
    - S3_ENABLED=true in .env
    - AWS credentials configured
    - Explicit user action to trigger

    By default, S3 is disabled and no data is sent to cloud.

    Args:
        thought_ids: List of thought IDs to export (None = export all)

    Returns:
        Export status and S3 location
    """
    from app.db.database import Database
    from app.utils.config import Config
    from app.services.s3_export import S3Exporter

    if not Config.S3_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="S3 export is disabled. To enable: set S3_ENABLED=true and provide AWS credentials in .env",
        )

    db = Database(Config.DB_PATH)
    exporter = S3Exporter(Config)

    if not exporter.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="S3 export configured but not available. Check AWS credentials.",
        )

    # Fetch thoughts to export
    if thought_ids:
        thoughts = [
            dict(db.get_thought(tid)) for tid in thought_ids
            if db.get_thought(tid)
        ]
    else:
        thoughts = db.get_all_thoughts(limit=10000)

    # Export to S3
    result = exporter.export_thoughts(thoughts)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result
