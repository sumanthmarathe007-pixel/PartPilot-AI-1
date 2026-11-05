from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


def main() -> int:
    base_url = os.getenv("PARTPILOT_GATEWAY_URL", "").rstrip("/")
    token = os.getenv("GATEWAY_TOKEN", "")
    if not base_url or not token:
        raise SystemExit("Set PARTPILOT_GATEWAY_URL and GATEWAY_TOKEN")

    payload = {
        "payload": {
            "requests": [{"request_id": "REQ-DEMO", "text": "12V USB-C, at least 10W"}],
            "parts": [{"part_id": "P-DEMO", "description": "12V USB-C 20W", "stock": "available", "freshness": "recent"}],
        }
    }
    req = Request(
        f"{base_url}/v1/plan",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Gateway-Token": token},
        method="POST",
    )
    with urlopen(req, timeout=45) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("inference") != "real" or not isinstance(result.get("plan"), dict):
        raise SystemExit(f"Unexpected gateway response: {result}")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
