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
    1. Stores the raw text in local SQLite
    2. Runs local Llama 3 for summarization
    3. Runs sentiment classification
    4. Returns results immediately (no cloud calls)

    Args:
        request: ThoughtRequest with raw_text

    Returns:
        Analyzed thought with summary and sentiment
    """
    from app.db.database import Database
    from app.utils.config import Config

    db = Database(Config.DB_PATH)

    # For now, store the thought
    thought_id = db.insert_thought(raw_text=request.raw_text)

    # LLM inference will be added in next steps
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

    This requires:
    - S3_ENABLED=true in .env
    - AWS credentials configured
    - Explicit user action

    Args:
        thought_ids: List of thought IDs to export (None = export all)

    Returns:
        Export status and S3 location
    """
    from app.utils.config import Config

    if not Config.S3_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="S3 export is disabled. Enable via S3_ENABLED=true in .env",
        )

    # S3 export logic will be implemented later
    return {
        "status": "export_queued",
        "count": len(thought_ids) if thought_ids else "all",
        "bucket": Config.S3_BUCKET_NAME,
    }
