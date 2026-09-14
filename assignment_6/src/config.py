"""
Configuration settings for the Background Job Service.
"""

import os

PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
INNGEST_APP_ID = "report-api"
