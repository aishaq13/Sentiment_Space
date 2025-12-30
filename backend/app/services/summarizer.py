"""
Summarization service.
Generates concise summaries of longer text using local Llama 3.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Summarizer:
    """
    Text summarization service using local Llama 3.
    Extracts key information from thoughts efficiently.
    """

    def __init__(self, llama_pipeline):
        """Initialize with LangChain pipeline."""
        self.pipeline = llama_pipeline

    def summarize(self, text: str, max_length: int = 150) -> Dict[str, Any]:
        """
        Summarize text to key points.

        Args:
            text: Text to summarize
            max_length: Maximum summary length in characters

        Returns:
            Dictionary with summary and metadata
        """
        if not text or len(text.strip()) < 20:
            return {
                "summary": text,
                "is_original": True,
                "reason": "Text too short to summarize"
            }

        summary = self.pipeline._summarize(text)

        return {
            "summary": summary[:max_length],
            "is_original": summary == text,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0,
        }
