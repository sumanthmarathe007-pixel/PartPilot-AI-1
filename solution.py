"""Competition entry point template.

This file is intentionally not submission-ready until protocol_adapter.py is
implemented from the organizer's exact API.md and OBSERVATIONS.md.
"""

from partpilot.protocol_adapter import (
    parse_observation,
    build_llm_action,
    build_world_action,
    parse_llm_result,
    OrganizerProtocolNotImplemented,
)


def decide(observation, state):
    """Organizer lifecycle entry point. Exact return contract must match API.md."""
    normalized = parse_observation(observation)

    # TODO: implement multi-turn lifecycle:
    # 1. If no LLM result is present, return organizer's exact op:llm action.
    # 2. When model text returns, parse structured plan and validate it.
    # 3. Choose one legal world action based on evidence and budget.
    # 4. Persist ledger/evidence/reservations in state.
    # 5. Return exact {action, state} envelope required by organizer.
    raise OrganizerProtocolNotImplemented(
        "Complete decide() against the organizer's actual API and state lifecycle."
    )
