"""
Configuration management for the LLM-powered API service.
Supports LiteLLM, Google GenAI SDK, and OpenAI compatible providers.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# LLM Provider Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "litellm")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini/gemini-3.1-flash-lite")

# Operational Controls
LLM_STUB = os.environ.get("LLM_STUB", "0").lower() in ("1", "true", "yes")
LLM_ENABLED = os.environ.get("LLM_ENABLED", "true").lower() in ("1", "true", "yes")
LLM_TIMEOUT = float(os.environ.get("LLM_TIMEOUT", "30.0"))

# Ensure LiteLLM picks up the GEMINI_API_KEY
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Directories
PROMPT_DIR = PROJECT_ROOT / "prompts"
LOGS_DIR = PROJECT_ROOT / "logs"
EVALS_DIR = PROJECT_ROOT / "evals"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
