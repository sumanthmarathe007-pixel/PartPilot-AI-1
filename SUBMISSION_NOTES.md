# Runtime and submission notes

## Competition runtime

The organizer specifies Python 3.12.14 and an allowlist of preinstalled packages.
This codebase intentionally uses Python's standard library in the controller and
in the optional hosted gateway. It does not need numpy, pandas, scipy,
scikit-learn, joblib, cloudpickle, python-dateutil, pytz, tzdata, six, or
threadpoolctl. Those packages are allowed by the organizer but are not required.

The competition controller must still be completed against the real API.md and
OBSERVATIONS.md. Do not guess action names, op:llm envelopes, state fields or
response lifecycle. The current protocol_adapter.py and solution.py retain TODOs.

## Do not submit as part of the evaluated controller unless explicitly required

- pytest (tests use unittest instead)
- FastAPI, Uvicorn, HTTPX, Pydantic, python-dotenv, google-genai
- any local virtual environment, .venv, API key, .env, cache or build artifacts

The gateway is deployed separately. This package's gateway/server.py uses
only the standard library and calls the Gemini REST API using urllib. The
organizer's controller should use the official op:llm lifecycle; it should not
make a direct HTTP request with gateway_client.py unless API.md explicitly says so.

## Run tests

    python -m unittest discover -s tests -v

## Run local gateway

PowerShell:

    $env:GEMINI_API_KEY = "..."
    $env:GATEWAY_TOKEN = "..."
    $env:GEMINI_MODEL = "<a model ID enabled for your API key>"
    python gateway/server.py

The hosting service provides the public HTTPS endpoint and forwards traffic to
PORT. Set the same secrets in its environment-variable settings.
