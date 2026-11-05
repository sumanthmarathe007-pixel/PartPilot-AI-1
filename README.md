# PartPilot AI — safety-first Agentic AI workshop controller

PartPilot is a development scaffold for the Workshop Parts Desk challenge. It separates LLM interpretation from deterministic Python safety and action control.

## Downloaded package contents

- `partpilot/`: normalized models, conservative parsing, compatibility checks, budget, evidence, inventory reservation, batch matching and policy helpers.
- `gateway/`: standard-library HTTP gateway that calls the Gemini REST API.
- `solution.py` and `partpilot/protocol_adapter.py`: deliberate organizer-integration TODOs.
- `tests/`: local tests of generic safety logic.
- `DEPLOYMENT.md`: Windows setup, local gateway test, GitHub and HTTPS deployment steps.
- `TEAM_RUNBOOK.md`: four-person ownership and integration checklist.

## Start here

1. Read `DEPLOYMENT.md`.
2. Read `TEAM_RUNBOOK.md` and assign file ownership.
3. Install Python dependencies and run `pytest -q`.
4. Set a Gemini API key and gateway token, then run the gateway locally.
5. Deploy the gateway over HTTPS.
6. Obtain the organizer's exact API and observation files.
7. Complete `partpilot/protocol_adapter.py` and `solution.py` using only the organizer's documented schemas.
8. Run the organizer's local runner and submit the frozen controller.

## Important: not yet an organizer-ready submission

The challenge brief does not include the actual `API.md`, `OBSERVATIONS.md`, organizer starter controller, or gateway example in this conversation. Therefore, the exact `op:llm` envelope, result field, action names/arguments, observation schema and state lifecycle are not known here. The adapter intentionally raises `OrganizerProtocolNotImplemented` rather than fabricating those fields.

The `gateway/server.py` implementation exposes a conventional authenticated `POST /v1/plan` route. The organizer may expect a different gateway protocol. Follow the organizer's provided gateway example and `API.md` if they differ. Do not replace the organizer's required `op:llm` action with a direct HTTP request unless its specification explicitly requires that.

## Safety invariants

- Unknown voltage, connector or wattage is not a match.
- Voltage and connector must match exactly unless authoritative catalogue evidence and organizer rules establish a valid alternative.
- Part wattage must be greater than or equal to the requested minimum.
- A 20W part can satisfy a 10W minimum.
- Recent stock snapshots are synchronized at batch opening as stated by the challenge.
- Aged stock requires authoritative verification before relying on availability.
- A part has only one unit; reserve it after successful dispatch confirmation.
- Keep shared tool usage within 14 units and actions within 60.
- Every request must end in dispatch or escalation.
- Any dispatch must pass deterministic Python validation; LLM text alone never authorizes it.

## Test status

The included generic test suite is expected to pass with:

```bash
pytest -q
```

These tests do not replace the official local runner. Use the exact current organizer command, including:

```bash
python local_runner.py solution.py smoke.json --mock
```

Only after the organizer adapter is completed.

## Strict-runtime version

For the organizer's Python 3.12.14 allowlisted runtime, this kit uses only the
Python standard library. No package installation is required. Run tests with:

    python -m unittest discover -s tests -v

The optional hosted gateway is implemented in `gateway/server.py`, also with
the standard library. Configure `GEMINI_API_KEY`, `GATEWAY_TOKEN`, and
`GEMINI_MODEL` through environment variables. The competition `solution.py`
remains incomplete until the exact organizer API/observation docs are applied.
