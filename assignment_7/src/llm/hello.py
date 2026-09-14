"""
Stage 0 Checkpoint: Basic provider connectivity test.
Queries the configured LLM using LiteLLM / Gemini to respond with 'ready'.
"""

import os
from dotenv import load_dotenv
import litellm

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY", "")
model = os.environ.get("LLM_MODEL", "gemini/gemini-3.1-flash-lite")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

response = litellm.completion(
    model=model,
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
    temperature=0.0,
)

print(response.choices[0].message.content.strip())
