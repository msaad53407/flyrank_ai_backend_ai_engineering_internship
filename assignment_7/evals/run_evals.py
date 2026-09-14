"""
Evaluation Runner for Support Message Triage.
Benchmarks 8 test cases against ground truth, measuring accuracy on category and urgency.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.llm.service import get_triage_decision, PROMPT_VERSION


EVALS_DIR = Path(__file__).resolve().parent
CASES_FILE = EVALS_DIR / "cases.json"
RESULTS_FILE = EVALS_DIR / "eval_results.json"


def run_evals():
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    print(f"=== Running Evaluation Suite on {len(cases)} Cases (Prompt {PROMPT_VERSION}) ===")

    total = len(cases)
    category_matches = 0
    urgency_matches = 0
    results = []

    start_time = time.perf_counter()

    for idx, c in enumerate(cases, start=1):
        case_id = c["id"]
        text = c["text"]
        exp_cat = c["expected_category"]
        exp_urg = c["expected_urgency"]

        print(f"\nEvaluating Case {idx}/{total} [{case_id}]...")
        decision = get_triage_decision(text, prompt_version=PROMPT_VERSION)

        cat_pass = (decision.category.value == exp_cat)
        urg_pass = (decision.urgency.value == exp_urg)

        if cat_pass:
            category_matches += 1
        if urg_pass:
            urgency_matches += 1

        status_emoji = "✅" if cat_pass else "❌"
        print(f"  {status_emoji} Category: {decision.category.value} (Expected: {exp_cat})")
        print(f"  Urgency:  {decision.urgency.value} (Expected: {exp_urg})")
        print(f"  Confidence: {decision.confidence:.2f} | Reason: {decision.reason}")

        results.append({
            "id": case_id,
            "text": text,
            "expected_category": exp_cat,
            "predicted_category": decision.category.value,
            "category_match": cat_pass,
            "expected_urgency": exp_urg,
            "predicted_urgency": decision.urgency.value,
            "urgency_match": urg_pass,
            "confidence": decision.confidence,
            "reason": decision.reason,
        })

    duration = round(time.perf_counter() - start_time, 2)
    cat_accuracy = (category_matches / total) * 100
    urg_accuracy = (urgency_matches / total) * 100

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": PROMPT_VERSION,
        "total_cases": total,
        "category_matches": category_matches,
        "category_accuracy_percent": cat_accuracy,
        "urgency_matches": urgency_matches,
        "urgency_accuracy_percent": urg_accuracy,
        "duration_seconds": duration,
        "details": results,
    }

    RESULTS_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"EVALUATION SUMMARY: {category_matches}/{total} Category Accuracy ({cat_accuracy:.1f}%)")
    print(f"Urgency Accuracy:   {urgency_matches}/{total} ({urg_accuracy:.1f}%)")
    print(f"Total Duration:     {duration}s")
    print(f"Results saved to:   {RESULTS_FILE}")
    print("=" * 60)

    return summary


if __name__ == "__main__":
    run_evals()
