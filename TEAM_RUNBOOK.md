# PartPilot AI — four-person team runbook

## Shared contract (agree before coding)

Use the data classes in `partpilot/models.py` as the internal contract. Keep these meanings fixed:

- `ElectricalSpec.voltage_v`: requested voltage for a request; rated voltage for a part.
- `ElectricalSpec.connector`: normalized connector name.
- `ElectricalSpec.min_wattage_w`: customer's minimum in a request; the part's rated watts in a part record.
- `None`: unknown; it is never a wildcard.
- `Freshness.RECENT`: snapshot is synchronized at batch opening under the challenge rules.
- `Freshness.AGED`: stock cannot be trusted until authoritative verification.

The structures in this scaffold are internal structures, not organizer wire-format structures.

## Member 1 — Gateway and LLM connection

Own:

- `gateway/app.py`
- `gateway/` deployment configuration
- `.env.example` (never commit `.env`)
- `scripts/check_gateway.py`

Acceptance criteria:

1. `GET /health` returns 200.
2. Requests without `X-Gateway-Token` return 401.
3. A valid authenticated request performs a real Gemini API inference.
4. Response includes a JSON `plan` object.
5. Provider key is stored only in host environment secrets.
6. Gateway is reachable over HTTPS before competition testing.
7. Logs show inference success/failure metadata without printing secrets or sensitive data.

## Member 2 — Language and catalogue interpretation

Own:

- `partpilot/parsing.py`
- `partpilot/prompts.py`

Acceptance criteria:

1. Parse explicit voltage, connector and wattage conservatively.
2. Distinguish customer minimum wattage from part rated wattage.
3. Represent missing requirements as `None`.
4. Record ambiguity instead of guessing.
5. Normalize aliases only when the catalogue/request makes equivalence explicit.
6. Include original wording/evidence for audit.
7. Test at least 10 different phrasings and missing-field cases.

## Member 3 — Safety, evidence, stock and allocation

Own:

- `partpilot/compatibility.py`
- `partpilot/budget.py`
- `partpilot/evidence.py`
- `partpilot/inventory.py`
- `partpilot/assignment.py`
- `partpilot/policy.py`
- `tests/test_core.py`

Acceptance criteria:

1. Exact voltage match unless organizer rules explicitly define otherwise.
2. Exact connector match unless the catalogue explicitly establishes an equivalent.
3. Part rated wattage must be >= customer minimum.
4. Unknown technical values fail closed.
5. Recent stock is treated according to the challenge's synchronized-at-open rule.
6. Aged stock is checked through `verify` before availability is relied upon.
7. Verified stock overrides stale snapshot evidence.
8. A part is reserved only after successful dispatch confirmation.
9. Never select a reserved part again.
10. Tool budget never goes below zero; maximum actions never exceeds 60.

## Member 4 — Organizer protocol and integration

Own:

- `solution.py`
- `partpilot/protocol_adapter.py`
- official runner integration
- final submission bundle

Acceptance criteria:

1. Exact `decide(observation, state)` signature and return object.
2. Exact `op:llm` request and response round trip.
3. Exact world action names and argument formats.
4. Correct lifecycle: one action per call if required by the API.
5. JSON-serializable state survives every call and resets correctly between batches.
6. Tool evidence is only recorded from actual organizer tool results.
7. No claim that dispatch succeeded until the organizer confirms it.
8. All six tickets end in dispatch or escalation.
9. Official local runner passes.

## Integration schedule

- T+0: everyone reads API/observation docs; agree internal schema.
- T+45m: each owner pushes a module skeleton and importable functions.
- T+90m: gateway inference works; parser and safety tests pass.
- T+120m: first shared branch merge.
- T+180m: organizer protocol end-to-end test.
- T+240m: run public smoke/training/practice and inspect diagnostics.
- T+300m: optimization and regression test.
- T+330m: freeze code and stop feature work.
- T+360m: submit and verify acceptance.

## Git workflow

Each teammate works on a branch. The integration owner reviews and merges pull requests. Do not edit the same file at the same time. Create an issue for interface changes and notify all owners before renaming a shared field.
