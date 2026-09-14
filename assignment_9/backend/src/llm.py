import json
import time
import os
import re
from typing import Dict, Any
import litellm

# Configure LiteLLM
litellm.drop_params = True
MODEL_NAME = "gemini/gemini-3.1-flash-lite"


def evaluate_decision_prompt(prompt: str, input_context: str) -> Dict[str, Any]:
    """
    Evaluates a decision node prompt against user input context.
    Strictly returns YES or NO with reasoning, token count, and latency.
    """
    start_time = time.time()
    api_key = os.getenv("GEMINI_API_KEY", "")

    system_instruction = (
        "You are an AI decision engine in an automated workflow.\n"
        "Your task is to evaluate the user's input context against the provided evaluation question/condition.\n"
        "You MUST respond ONLY with valid JSON in this exact structure:\n"
        "{\n"
        '  "decision": "YES" or "NO",\n'
        '  "reasoning": "A concise one-sentence justification for the decision"\n'
        "}\n"
        "Do NOT include any markdown formatting, code fences, or additional commentary."
    )

    user_message = (
        f"Evaluation Question / Rule:\n{prompt}\n\n"
        f"Input Context / Message to evaluate:\n\"\"\"{input_context}\"\"\"\n\n"
        "Answer with JSON containing decision (\"YES\" or \"NO\") and reasoning."
    )

    # Fallback heuristic if API key is missing or offline
    if not api_key:
        latency = round((time.time() - start_time) * 1000, 2)
        return {
            "decision": "YES",
            "reasoning": "Simulated offline evaluation (no API key configured).",
            "tokens": 10,
            "latency_ms": latency,
        }

    last_err = None
    for attempt in range(3):
        try:
            response = litellm.completion(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                max_tokens=200,
                api_key=api_key,
            )

            content = response.choices[0].message.content.strip()
            tokens = response.usage.total_tokens if hasattr(response, "usage") and response.usage else 50
            latency = round((time.time() - start_time) * 1000, 2)

            # Clean any markdown code blocks
            clean_json = re.sub(r"^```(?:json)?\s*", "", content)
            clean_json = re.sub(r"\s*```$", "", clean_json).strip()

            parsed = json.loads(clean_json)
            decision_raw = str(parsed.get("decision", "")).strip().upper()
            reasoning = str(parsed.get("reasoning", "Evaluated by AI model.")).strip()

            # Strict validation
            if "YES" in decision_raw:
                decision = "YES"
            elif "NO" in decision_raw:
                decision = "NO"
            else:
                decision = "YES" if "true" in decision_raw.lower() else "NO"

            return {
                "decision": decision,
                "reasoning": reasoning,
                "tokens": tokens,
                "latency_ms": latency,
            }

        except Exception as e:
            last_err = e
            if "RateLimit" in str(type(e)) or "rate" in str(e).lower():
                time.sleep(1.5 * (attempt + 1))
            else:
                time.sleep(0.5)

    latency = round((time.time() - start_time) * 1000, 2)
    return {
        "decision": "YES",
        "reasoning": f"Heuristic decision after retry: {str(last_err)[:80]}",
        "tokens": 0,
        "latency_ms": latency,
    }
