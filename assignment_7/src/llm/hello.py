"""
Stage 0 Checkpoint: Basic provider connectivity test.
Queries the configured LLM to respond with 'ready'.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

base_url = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1/")
api_key = os.environ.get("LLM_API_KEY", "ollama")
model = os.environ.get("LLM_MODEL", "orieg/gemma3-tools:1b")

client = OpenAI(base_url=base_url, api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
    temperature=0.0,
)

print(response.choices[0].message.content)
