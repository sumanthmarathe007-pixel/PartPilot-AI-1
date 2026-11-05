"""Standard-library-only PartPilot Gemini gateway.

Run: python gateway/server.py
The hosting platform should terminate public HTTPS and forward to PORT.
No third-party Python packages are required by this gateway.
"""
from __future__ import annotations
from urllib.parse import urlsplit
import hmac
import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from partpilot.prompts import SYSTEM_PROMPT, build_user_prompt  # noqa: E402

LOG = logging.getLogger("partpilot.gateway")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def _json_response(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(raw)


def _call_gemini(payload: dict) -> tuple[dict, str]:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model = os.environ.get("GEMINI_MODEL", "")
    api_version = os.environ.get("GEMINI_API_VERSION", "v1beta")
    if not api_key or not model:
        raise RuntimeError("GEMINI_API_KEY and GEMINI_MODEL must be configured")

    endpoint = (
        "https://generativelanguage.googleapis.com/"
        f"{api_version}/models/{quote(model, safe='')}:generateContent"
    )
    request_body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": build_user_prompt(payload)}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }
    req = Request(
        endpoint,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urlopen(req, timeout=40) as response:
        result = json.loads(response.read().decode("utf-8"))

    texts = []
    for candidate in result.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            if isinstance(part.get("text"), str):
                texts.append(part["text"])
        if texts:
            break
    if not texts:
        raise ValueError("Gemini response did not contain candidate text")

    model_text = "\n".join(texts).strip()
    plan = json.loads(model_text)
    if not isinstance(plan, dict):
        raise ValueError("Gemini response must be a JSON object")
    return plan, model


class Handler(BaseHTTPRequestHandler):
    server_version = "PartPilotGateway/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Log request metadata, not request bodies, API keys or authorization headers.
        LOG.info("%s - %s", self.address_string(), fmt % args)

    def do_GET(self) -> None:  # noqa: N802
        if urlsplit(self.path).path.rstrip("/") == "/health":
            _json_response(self, 200, {"status": "ok", "service": "partpilot-gateway"})
        else:
            _json_response(self, 404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if urlsplit(self.path).path.rstrip("/") == "/v1/plan":
            _json_response(self, 404, {"error": "not_found"})
            return

        expected = os.environ.get("GATEWAY_TOKEN", "")
        supplied = self.headers.get("X-Gateway-Token", "")
        if not expected or not hmac.compare_digest(expected, supplied):
            _json_response(self, 401, {"error": "unauthorized"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                _json_response(self, 400, {"error": "invalid_content_length"})
                return
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict) or not isinstance(body.get("payload"), dict):
                _json_response(self, 400, {"error": "payload_must_be_object"})
                return
            plan, model = _call_gemini(body["payload"])
            LOG.info("inference_success model=%s keys=%s", model, sorted(body["payload"].keys()))
            _json_response(self, 200, {"plan": plan, "model": model, "inference": "real"})
        except HTTPError as exc:
            LOG.error("Gemini HTTP error status=%s", exc.code)
            _json_response(self, 502, {"error": "model_provider_http_error", "status": exc.code})
        except (URLError, TimeoutError) as exc:
            LOG.error("Gemini network error type=%s", type(exc).__name__)
            _json_response(self, 502, {"error": "model_provider_network_error"})
        except (ValueError, json.JSONDecodeError) as exc:
            LOG.error("Invalid request/model JSON type=%s", type(exc).__name__)
            _json_response(self, 400, {"error": "invalid_json_or_model_response"})
        except Exception as exc:  # defensive gateway boundary
            LOG.exception("Gateway inference failed type=%s", type(exc).__name__)
            _json_response(self, 502, {"error": "inference_failed"})


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), Handler)
    LOG.info("PartPilot standard-library gateway listening on %s:%s", host, port)
    server.serve_forever()


if __name__ == "__main__":
    main()
