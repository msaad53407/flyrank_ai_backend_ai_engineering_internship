"""
Inngest background job functions:
1. say-hello: Simple 5s background greeting.
2. make-report: Durable 8s report generator with retries and failure simulation.
3. heartbeat: Cron task executing on schedule (* * * * *).
"""

import datetime
import inngest
from src.inngest_client import inngest_client
from src.storage import get_counts, update_report


@inngest_client.create_function(
    fn_id="say-hello",
    name="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context, step: inngest.Step) -> str:
    """Introductory background task that sleeps 5 seconds then returns greeting."""
    await step.sleep("wait-a-bit", datetime.timedelta(seconds=5))
    return "Hello from the background!"


@inngest_client.create_function(
    fn_id="make-report",
    name="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,  # Stage 3 requirement: 2 retries (3 total attempts) with backoff
)
async def make_report(ctx: inngest.Context, step: inngest.Step) -> dict:
    """
    Durable multi-step report generation pipeline:
    1. step.sleep('do-the-slow-work', 8s) - simulated heavy compute/export.
    2. step.run('build-report') - builds report or triggers retry error if topic == 'fail'.
    """
    event_data = ctx.event.data or {}
    report_id = event_data.get("id")
    topic = event_data.get("topic", "")

    # Step 1: Simulated slow computation (8 seconds)
    await step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    # Step 2: Build report
    async def _build():
        # Failure simulation for Stage 3 checkpoint
        if topic == "fail":
            update_report(report_id, status="failed", result="Error: The report oven is broken!")
            raise Exception("The report oven is broken!")

        result_text = f"Comprehensive executive intelligence report compiled for topic: '{topic}'."
        update_report(report_id, status="done", result=result_text)
        return {"report_id": report_id, "topic": topic, "status": "done", "result": result_text}

    return await step.run("build-report", _build)


@inngest_client.create_function(
    fn_id="heartbeat",
    name="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),  # Stage 4 requirement: every minute
)
async def heartbeat(ctx: inngest.Context, step: inngest.Step) -> dict:
    """Scheduled cron task executing every minute without an incoming HTTP request."""
    counts = get_counts()
    summary_line = (
        f"[HEARTBEAT] Reports summary: pending={counts['pending']}, "
        f"done={counts['done']}, failed={counts['failed']}, total={counts['total']}"
    )
    print(summary_line)
    return counts
