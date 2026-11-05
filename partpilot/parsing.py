from __future__ import annotations

import re
from .models import ElectricalSpec

# Keep this small and explicit. Expand only when catalogue/request examples justify it.
_CONNECTOR_ALIASES = {
    "usb c": "usb-c",
    "usb-c": "usb-c",
    "type c": "usb-c",
    "usb type c": "usb-c",
    "usb a": "usb-a",
    "usb-a": "usb-a",
    "barrel jack": "barrel",
    "dc barrel": "barrel",
}


def normalize_connector(value: str | None) -> str | None:
    if not value:
        return None
    compact = re.sub(r"\s+", " ", value.strip().lower())
    return _CONNECTOR_ALIASES.get(compact, compact)


def parse_spec_fallback(text: str) -> ElectricalSpec:
    """Conservative regex fallback. It must not guess values absent from the text."""
    raw = text or ""
    lower = raw.lower()

    voltage = None
    wattage = None
    connector = None

    vm = re.search(r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:v|volt|volts)\b", lower)
    if vm:
        voltage = float(vm.group(1))

    # Match minimum/at-least wattage, but also accept an unqualified W rating
    # when parsing a catalogue part description.
    wm = re.search(
        r"(?:at\s+least|min(?:imum)?\s*)?(\d+(?:\.\d+)?)\s*(?:w|watt|watts)\b",
        lower,
    )
    if wm:
        wattage = float(wm.group(1))

    for known in (
        "usb type c", "usb-c", "usb c", "type c",
        "usb-a", "usb a", "barrel jack", "dc barrel",
    ):
        if known in lower:
            connector = normalize_connector(known)
            break

    return ElectricalSpec(
        voltage_v=voltage,
        connector=connector,
        min_wattage_w=wattage,
        raw_text=raw,
        confidence={
            "voltage_v": 0.95 if voltage is not None else 0.0,
            "connector": 0.90 if connector is not None else 0.0,
            "min_wattage_w": 0.90 if wattage is not None else 0.0,
        },
    )


def merge_llm_spec(raw_text: str, llm_json: dict) -> ElectricalSpec:
    """Validate/normalize fields extracted by the LLM; invalid values stay unknown."""
    def positive_number(key: str):
        value = llm_json.get(key)
        try:
            number = float(value)
            return number if number > 0 else None
        except (TypeError, ValueError):
            return None

    conf = llm_json.get("confidence") or {}
    if not isinstance(conf, dict):
        conf = {}

    return ElectricalSpec(
        voltage_v=positive_number("voltage_v"),
        connector=normalize_connector(llm_json.get("connector")),
        min_wattage_w=positive_number("min_wattage_w"),
        ambiguous_fields=list(llm_json.get("ambiguous_fields") or []),
        raw_text=raw_text,
        confidence={
            "voltage_v": float(conf.get("voltage_v", 0.0) or 0.0),
            "connector": float(conf.get("connector", 0.0) or 0.0),
            "min_wattage_w": float(conf.get("min_wattage_w", 0.0) or 0.0),
        },
    )
