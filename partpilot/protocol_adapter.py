"""Organizer-specific mapping layer — complete this after reading API.md.

Do not guess action names, field names, or the LLM round-trip format.
The organizer brief says the controller emits op:llm and then chooses a world
action using returned model text, but the exact envelope belongs to API.md.
"""


class OrganizerProtocolNotImplemented(RuntimeError):
    pass


def parse_observation(observation: dict) -> dict:
    """TODO: map exact v6 observation fields into normalized internal payload.

    Return a dict with at least:
      - batch_id or equivalent
      - requests: list of {request_id, text}
      - parts: list of {part_id, description, stock_snapshot, freshness}
      - available_actions/tool descriptions as supplied by organizer
      - returned LLM response fields, if this is an LLM-resumption call
    """
    raise OrganizerProtocolNotImplemented("Map observation using the organizer's OBSERVATIONS.md")


def build_llm_action(payload: dict) -> dict:
    """TODO: return the exact organizer op:llm action envelope from API.md."""
    raise OrganizerProtocolNotImplemented("Map op:llm action using organizer API.md")


def build_world_action(kind: str, args: dict) -> dict:
    """TODO: construct exact inspect/clarify/verify/dispatch/escalate action."""
    raise OrganizerProtocolNotImplemented("Map world action schema using organizer API.md")


def parse_llm_result(observation: dict) -> str:
    """TODO: retrieve exact model text/result field from the resumed observation."""
    raise OrganizerProtocolNotImplemented("Map LLM return field using organizer API.md")
