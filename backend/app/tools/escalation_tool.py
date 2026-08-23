import asyncio
import secrets
import uuid
from dataclasses import dataclass

# Getnet's general customer-service line. The official site blocks direct
# fetches (see design.md), so this was cross-checked against several
# independent consumer-service directories rather than the source itself -
# swap for the confirmed number if it ever needs to be authoritative.
GETNET_SUPPORT_PHONE = "0800 648 8000"


@dataclass(frozen=True)
class HandoffConfirmation:
    ticket_id: str
    queue_position: int
    estimated_wait_minutes: int


@dataclass(frozen=True)
class PhoneTransferConfirmation:
    phone_number: str
    access_code: str


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


async def default_mock_phone_transfer_call(message: str, user_id: str) -> PhoneTransferConfirmation:
    """Stand-in for a real IVR/phone-transfer system call: generates a
    one-time code the user reads back over the phone to skip the queue and
    reach a specialist directly. Swappable, same shape as the chat handoff
    above."""
    await asyncio.sleep(0)
    return PhoneTransferConfirmation(
        phone_number=GETNET_SUPPORT_PHONE,
        access_code=f"{secrets.randbelow(1_000_000):06d}",
    )
