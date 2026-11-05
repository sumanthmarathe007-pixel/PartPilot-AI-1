"""Standard-library client for local gateway tests, not the organizer op:llm path."""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GatewayError(RuntimeError):
    pass


def request_plan(payload: dict, timeout_seconds: float = 25.0) -> dict:
    base_url = os.getenv("PARTPILOT_GATEWAY_URL", "").rstrip("/")
    token = os.getenv("GATEWAY_TOKEN", "")
    if not base_url or not token:
        raise GatewayError("PARTPILOT_GATEWAY_URL and GATEWAY_TOKEN must be configured")

    request = Request(
        f"{base_url}/v1/plan",
        data=json.dumps({"payload": payload}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Gateway-Token": token,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise GatewayError(f"Gateway request failed: {type(exc).__name__}: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("plan"), dict):
        raise GatewayError("Gateway response missing object field 'plan'")
    return data["plan"]
