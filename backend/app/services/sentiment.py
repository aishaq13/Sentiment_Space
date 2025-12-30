"""
Sentiment analysis service.
Wraps LLM inference for sentiment classification with caching.
"""

import logging
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analysis service using local Llama 3.
    Provides caching for repeated queries.
    """

    # Sentiment keywords for fallback classification
    POSITIVE_KEYWORDS = {
        "good", "great", "happy", "excellent", "love", "perfect",
        "wonderful", "amazing", "awesome", "fantastic"
    }
    NEGATIVE_KEYWORDS = {
        "bad", "awful", "sad", "terrible", "hate", "horrible",
        "awful", "disgusting", "poor", "worst"
    }

    def __init__(self, llama_pipeline):
        """Initialize with LangChain pipeline."""
        self.pipeline = llama_pipeline

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment, confidence, and explanation
        """
        if not text or len(text.strip()) == 0:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "explanation": "Text is empty"
            }

        result = self.pipeline._classify_sentiment(text)
        confidence = self.pipeline._estimate_confidence(text, result)

        return {
            "sentiment": result,
            "confidence": confidence,
            "explanation": self._get_explanation(result, text),
        }

    def _get_explanation(self, sentiment: str, text: str) -> str:
        """Get explanation for sentiment classification."""
        text_lower = text.lower()

        if sentiment == "positive":
            return "Contains positive language and optimistic tone"
        elif sentiment == "negative":
            return "Contains negative language or critical tone"
        else:
            return "Neutral or balanced sentiment"

    @lru_cache(maxsize=128)
    def get_cached_sentiment(self, text_hash: int) -> Optional[str]:
        """
        Get cached sentiment if available.

        Args:
            text_hash: Hash of text

        Returns:
            Cached sentiment or None
        """
        # Placeholder for cache implementation
        return None
