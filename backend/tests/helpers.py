import json


def parse_sse(body: str) -> list[dict]:
    """Turn a Server-Sent Events body into a list of event dicts."""
    events = []
    for block in body.split("\n\n"):
        if block.startswith("data: "):
            events.append(json.loads(block.removeprefix("data: ")))
    return events
