import asyncio
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class HandoffConfirmation:
    ticket_id: str
    queue_position: int
    estimated_wait_minutes: int


async def default_mock_handoff_call(message: str, user_id: str) -> HandoffConfirmation:
    """Stand-in for a real human-handoff/CRM system call. Swappable (see
    EscalationAgent's constructor) so it's trivial to point at a real
    system later without touching the agent's control flow, and trivial
    to mock in tests."""
    await asyncio.sleep(0)
    return HandoffConfirmation(
        ticket_id=f"ESC-{uuid.uuid4().hex[:8].upper()}",
        queue_position=1,
        estimated_wait_minutes=5,
    )
