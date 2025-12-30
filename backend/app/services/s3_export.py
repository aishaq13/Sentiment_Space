"""
AWS S3 export service for optional thought backup.
Completely optional and disabled by default.

Design Principle: Privacy-first with explicit user consent
- S3 is disabled by default (S3_ENABLED=false)
- Requires AWS credentials in .env
- User must explicitly call /export endpoint
- No automatic syncing
- Works fully offline without AWS
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class S3Exporter:
    """
    Handle optional S3 exports for thought backups.
    Respects privacy-first design: disabled by default.
    """

    def __init__(self, config):
        """
        Initialize S3 exporter.

        Args:
            config: Configuration object with AWS settings
        """
        self.config = config
        self.s3_client = None

        if config.S3_ENABLED:
            self._init_s3_client()

    def _init_s3_client(self):
        """Initialize boto3 S3 client if enabled and credentials available."""
        if not self.config.S3_ENABLED:
            logger.info("S3 export is disabled")
            return

        try:
            import boto3

            self.s3_client = boto3.client(
                "s3",
                region_name=self.config.AWS_REGION,
                aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
            )
            logger.info(f"S3 client initialized for bucket: {self.config.S3_BUCKET_NAME}")
        except ImportError:
            logger.warning(
                "boto3 not installed. S3 export unavailable. "
                "Install with: pip install boto3"
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")

    def export_thoughts(
        self,
        thoughts: List[Dict[str, Any]],
        prefix: str = "exports",
    ) -> Dict[str, Any]:
        """
        Export thoughts to S3.

        Privacy considerations:
        - User explicitly requested this export
        - Data is encrypted in transit (HTTPS)
        - User controls bucket and credentials
        - Can be disabled entirely in .env

        Args:
            thoughts: List of thought dictionaries
            prefix: S3 path prefix

        Returns:
            Export status and S3 location
        """
        if not self.config.S3_ENABLED:
            return {
                "success": False,
                "error": "S3 export is disabled. Set S3_ENABLED=true in .env to enable.",
            }

        if not self.s3_client:
            return {
                "success": False,
                "error": "S3 client not initialized. Check AWS credentials.",
            }

        try:
            # Prepare export data
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "thought_count": len(thoughts),
                "thoughts": thoughts,
            }

            # Generate S3 key
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f"{prefix}/thoughts_export_{timestamp}.json"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.config.S3_BUCKET_NAME,
                Key=key,
                Body=json.dumps(export_data, indent=2),
                ContentType="application/json",
            )

            logger.info(f"Exported {len(thoughts)} thoughts to s3://{self.config.S3_BUCKET_NAME}/{key}")

            return {
                "success": True,
                "bucket": self.config.S3_BUCKET_NAME,
                "key": key,
                "thought_count": len(thoughts),
                "url": f"s3://{self.config.S3_BUCKET_NAME}/{key}",
            }

        except Exception as e:
            logger.error(f"S3 export failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def is_enabled(self) -> bool:
        """Check if S3 export is enabled and available."""
        return self.config.S3_ENABLED and self.s3_client is not None

    def get_bucket_info(self) -> Dict[str, Any]:
        """Get information about configured S3 bucket."""
        return {
            "enabled": self.config.S3_ENABLED,
            "bucket": self.config.S3_BUCKET_NAME,
            "region": self.config.AWS_REGION,
            "available": self.s3_client is not None,
        }
