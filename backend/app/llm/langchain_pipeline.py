"""
LangChain pipeline for orchestrating sentiment analysis and summarization.
Combines local Llama 3 with prompt templates and memory management.

Architecture:
- Uses LangChain PromptTemplate for structured prompts
- Chains multiple operations: input -> summarization -> sentiment
- Memory system tracks conversation context
- All operations run locally (no cloud APIs)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SentimentAnalysisPipeline:
    """
    Orchestrates sentiment analysis and summarization using LangChain.
    Chains together multiple operations with local LLM inference.
    """

    # Summarization prompt template
    SUMMARIZE_PROMPT = """Please provide a concise summary (1-2 sentences) of the following thought:

Thought: {text}

Summary:"""

    # Sentiment analysis prompt template
    SENTIMENT_PROMPT = """Analyze the sentiment of the following text.
Respond with ONLY one word: positive, neutral, or negative.

Text: {text}

Sentiment:"""

    # Confidence estimation prompt
    CONFIDENCE_PROMPT = """On a scale of 0-1, how confident are you in the sentiment of this text? Respond with only a number.

Text: {text}

Confidence (0-1):"""

    def __init__(self, llama_loader):
        """
        Initialize pipeline with Llama loader.

        Args:
            llama_loader: LlamaLoader instance with loaded model
        """
        self.llama_loader = llama_loader
        self.memory: List[Dict[str, Any]] = []
        logger.info("Initialized SentimentAnalysisPipeline")

    def analyze(
        self, raw_text: str, track_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Full analysis pipeline: summarization + sentiment + confidence.

        Args:
            raw_text: Input text to analyze
            track_memory: Whether to store in memory for context

        Returns:
            Dictionary with summary, sentiment, and confidence
        """
        logger.info(f"Analyzing text: {raw_text[:50]}...")

        # Step 1: Generate summary
        summary = self._summarize(raw_text)

        # Step 2: Analyze sentiment
        sentiment = self._classify_sentiment(raw_text)

        # Step 3: Estimate confidence
        confidence = self._estimate_confidence(raw_text, sentiment)

        result = {
            "summary": summary,
            "sentiment": sentiment,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

        # Track in memory for context
        if track_memory:
            self.memory.append({"text": raw_text, **result})
            logger.info(f"Stored in memory. Total entries: {len(self.memory)}")

        return result

    def _summarize(self, text: str) -> str:
        """
        Generate summary using Llama 3.

        Why local inference:
        - No cloud API latency
        - Instant response
        - Privacy preserved
        """
        if len(text) < 10:
            return text

        prompt = self.SUMMARIZE_PROMPT.format(text=text[:512])
        summary = self.llama_loader.generate(
            prompt, max_new_tokens=100, temperature=0.3
        )

        # Clean up response
        summary = summary.split("\n")[0].strip()
        return summary if summary else text[:100]

    def _classify_sentiment(self, text: str) -> str:
        """
        Classify sentiment using Llama 3.

        Local inference advantages:
        - Runs on CPU instantly
        - No network overhead
        - Works offline
        """
        prompt = self.SENTIMENT_PROMPT.format(text=text[:512])
        response = self.llama_loader.generate(
            prompt, max_new_tokens=10, temperature=0.1
        )

        sentiment = response.strip().lower()
        valid_sentiments = ["positive", "neutral", "negative"]

        if sentiment not in valid_sentiments:
            logger.warning(f"Invalid sentiment response: {response}")
            return "neutral"

        return sentiment

    def _estimate_confidence(self, text: str, sentiment: str) -> float:
        """
        Estimate model confidence in sentiment classification.
        """
        prompt = self.CONFIDENCE_PROMPT.format(text=text[:512])
        response = self.llama_loader.generate(
            prompt, max_new_tokens=5, temperature=0.1
        )

        try:
            confidence = float(response.strip())
            return max(0.0, min(1.0, confidence))
        except ValueError:
            logger.warning(f"Failed to parse confidence: {response}")
            return 0.5

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of stored memory for context awareness.

        Returns:
            Statistics about analyzed thoughts
        """
        if not self.memory:
            return {"total_entries": 0, "sentiments": {}}

        sentiments = {}
        for entry in self.memory:
            s = entry.get("sentiment", "neutral")
            sentiments[s] = sentiments.get(s, 0) + 1

        return {
            "total_entries": len(self.memory),
            "sentiments": sentiments,
            "last_analyzed": (
                self.memory[-1].get("timestamp") if self.memory else None
            ),
        }

    def clear_memory(self) -> None:
        """Clear memory (e.g., at end of session)."""
        self.memory.clear()
        logger.info("Cleared pipeline memory")

    def get_similar_thoughts(
        self, text: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find similar thoughts in memory based on text similarity.
        Simple implementation using word overlap.

        Args:
            text: Query text
            limit: Maximum results

        Returns:
            List of similar thoughts from memory
        """
        if not self.memory:
            return []

        query_words = set(text.lower().split())

        scored = []
        for entry in self.memory:
            entry_words = set(entry["text"].lower().split())
            overlap = len(query_words & entry_words)
            if overlap > 0:
                scored.append((entry, overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in scored[:limit]]
