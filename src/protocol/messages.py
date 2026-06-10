"""Message dataclasses and field metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

MESSAGE_1_FORMAT = "!ii25sI25sh"
MESSAGE_1_SIZE = 64
MESSAGE_2_FORMAT = "!iibqqi"
MESSAGE_2_SIZE = 29

RANK_LABELS: dict[int, str] = {
    0: "First Lieutenant",
    1: "Lieutenant",
    2: "Second Lieutenant",
}


@dataclass(frozen=True)
class Message1:
    message_id: int
    unit_reference_no: int
    first_name: str
    unit_no: int
    last_name: str
    rank: int


@dataclass(frozen=True)
class Message2:
    message_id: int
    unit_reference_no: int
    position_validity: int
    latitude: int
    longitude: int
    altitude: int


Message = Message1 | Message2

FieldType = Literal["int", "string", "uint", "short", "bool", "long"]


@dataclass(frozen=True)
class FieldDefinition:
    ui_label: str
    internal_name: str
    field_type: FieldType
    editable: bool = True
    min_value: int | None = None
    max_value: int | None = None
    byte_length: int | None = None
    dropdown_options: dict[int, str] | None = None
    fixed_value: int | None = None


MESSAGE_DEFINITIONS: dict[int, list[FieldDefinition]] = {
    1: [
        FieldDefinition("Message ID", "message_id", "int", editable=False, fixed_value=1),
        FieldDefinition(
            "Unit Reference No",
            "unit_reference_no",
            "int",
            min_value=-1000,
            max_value=9999,
        ),
        FieldDefinition(
            "First Name",
            "first_name",
            "string",
            byte_length=25,
        ),
        FieldDefinition(
            "Unit No",
            "unit_no",
            "uint",
            min_value=0,
            max_value=4294967295,
        ),
        FieldDefinition(
            "Last Name",
            "last_name",
            "string",
            byte_length=25,
        ),
        FieldDefinition(
            "Rank",
            "rank",
            "short",
            min_value=0,
            max_value=2,
            dropdown_options=RANK_LABELS,
        ),
    ],
    2: [
        FieldDefinition("Message ID", "message_id", "int", editable=False, fixed_value=2),
        FieldDefinition(
            "Unit Reference No",
            "unit_reference_no",
            "int",
            min_value=1,
            max_value=9999,
        ),
        FieldDefinition(
            "Position Valid",
            "position_validity",
            "bool",
            min_value=0,
            max_value=1,
        ),
        FieldDefinition(
            "Latitude",
            "latitude",
            "long",
            min_value=-32400000,
            max_value=32400000,
        ),
        FieldDefinition(
            "Longitude",
            "longitude",
            "long",
            min_value=-64800000,
            max_value=64800000,
        ),
        FieldDefinition(
            "Altitude",
            "altitude",
            "int",
            min_value=0,
            max_value=10000,
        ),
    ],
}


def get_message_type_label(message_id: int) -> str:
    """Return UI label for a message type."""
    labels = {1: "Message 1 — Personnel", 2: "Message 2 — Unit Position"}
    return labels.get(message_id, f"Unknown Message ({message_id})")


def get_message_short_label(message_id: int) -> str:
    """Return short log label for a message type."""
    return f"Message {message_id}"


def field_range_hint(field_def: FieldDefinition) -> str:
    """Human-readable allowed range for tooltips."""
    if not field_def.editable and field_def.fixed_value is not None:
        return f"Fixed value: {field_def.fixed_value}"

    if field_def.field_type == "string" and field_def.byte_length:
        return f"UTF-8 text, max {field_def.byte_length} bytes"

    if field_def.dropdown_options:
        labels = ", ".join(f"{k}={v}" for k, v in field_def.dropdown_options.items())
        return f"Options: {labels}"

    if field_def.field_type == "bool":
        return "0 = Invalid · 1 = Valid"

    if field_def.min_value is not None and field_def.max_value is not None:
        return f"Allowed range: {field_def.min_value} – {field_def.max_value}"

    if field_def.min_value is not None:
        return f"Minimum: {field_def.min_value}"

    if field_def.max_value is not None:
        return f"Maximum: {field_def.max_value}"

    return ""


def message_to_dict(message: Message) -> dict[str, Any]:
    """Convert a message dataclass to a display-friendly dict."""
    if isinstance(message, Message1):
        return {
            "Message ID": message.message_id,
            "Unit Reference No": message.unit_reference_no,
            "First Name": message.first_name,
            "Unit No": message.unit_no,
            "Last Name": message.last_name,
            "Rank": f"{message.rank} — {RANK_LABELS.get(message.rank, '?')}",
        }
    return {
        "Message ID": message.message_id,
        "Unit Reference No": message.unit_reference_no,
        "Position Valid": "Valid ✓" if message.position_validity else "Invalid ✗",
        "Latitude": message.latitude,
        "Longitude": message.longitude,
        "Altitude": message.altitude,
    }
