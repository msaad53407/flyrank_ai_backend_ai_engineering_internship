"""
Configuration management for the LLM-powered API service.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# LLM Provider Configuration
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "ollama")
LLM_MODEL = os.environ.get("LLM_MODEL", "orieg/gemma3-tools:1b")

# Operational Controls
LLM_STUB = os.environ.get("LLM_STUB", "0").lower() in ("1", "true", "yes")
LLM_ENABLED = os.environ.get("LLM_ENABLED", "true").lower() in ("1", "true", "yes")
LLM_TIMEOUT = float(os.environ.get("LLM_TIMEOUT", "30.0"))

# Directories
PROMPT_DIR = PROJECT_ROOT / "prompts"
LOGS_DIR = PROJECT_ROOT / "logs"
EVALS_DIR = PROJECT_ROOT / "evals"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
