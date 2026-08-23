import uuid


def new_trace_id() -> str:
    """One unique id per /chat request, generated before anything else runs
    so it's present even on a guardrail rejection."""
    return str(uuid.uuid4())
