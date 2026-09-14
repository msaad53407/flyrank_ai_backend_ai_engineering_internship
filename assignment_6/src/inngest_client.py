"""
Inngest client initialization.
"""

import os
import inngest
from src.config import INNGEST_APP_ID

# Initialize Inngest client with local dev mode enabled (no signing key required)
inngest_client = inngest.Inngest(
    app_id=INNGEST_APP_ID,
    is_production=os.environ.get("INNGEST_IS_PRODUCTION", "false").lower() == "true",
)
