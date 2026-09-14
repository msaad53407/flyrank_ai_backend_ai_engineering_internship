import os
from pathlib import Path
from dotenv import load_dotenv
import inngest

# Locate backend root
BACKEND_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BACKEND_DIR / "static"
DB_PATH = BACKEND_DIR / "workflows.db"

# Load .env file
load_dotenv(BACKEND_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

INNGEST_APP_ID = "ai-decision-flow"

# Configure Inngest client (dev mode with is_production=False)
inngest_client = inngest.Inngest(
    app_id=INNGEST_APP_ID,
    is_production=False,
)
