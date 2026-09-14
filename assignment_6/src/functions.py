"""
Inngest background job functions.
"""

import datetime
import inngest
from src.inngest_client import inngest_client


@inngest_client.create_function(
    fn_id="say-hello",
    name="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context, step: inngest.Step) -> str:
    """Introductory background task that sleeps 5 seconds then returns greeting."""
    await step.sleep("wait-a-bit", datetime.timedelta(seconds=5))
    return "Hello from the background!"
