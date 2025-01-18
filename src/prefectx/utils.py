import uuid

def unique_name(s: str) -> str:
    return f"{s}-{uuid.uuid4().hex[:8]}"