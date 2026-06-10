"""Message dataclasses and field metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

MESSAGE_1_FORMAT = "!ii25sI25sh"
MESSAGE_1_SIZE = 64
MESSAGE_2_FORMAT = "!iibqqi"
MESSAGE_2_SIZE = 29

RANK_LABELS: dict[int, str] = {
    0: "Üsteğmen",
    1: "Teğmen",
    2: "Asteğmen",
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
        FieldDefinition("Mesaj ID", "message_id", "int", editable=False, fixed_value=1),
        FieldDefinition(
            "Birlik Referans Numarası",
            "unit_reference_no",
            "int",
            min_value=-1000,
            max_value=9999,
        ),
        FieldDefinition(
            "Adı",
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
            "Soyadı",
            "last_name",
            "string",
            byte_length=25,
        ),
        FieldDefinition(
            "Rütbe",
            "rank",
            "short",
            min_value=0,
            max_value=2,
            dropdown_options=RANK_LABELS,
        ),
    ],
    2: [
        FieldDefinition("Mesaj ID", "message_id", "int", editable=False, fixed_value=2),
        FieldDefinition(
            "Birlik Referans Numarası",
            "unit_reference_no",
            "int",
            min_value=1,
            max_value=9999,
        ),
        FieldDefinition(
            "Birlik Konum Bilgisi Geçerliliği",
            "position_validity",
            "bool",
            min_value=0,
            max_value=1,
        ),
        FieldDefinition(
            "Enlem",
            "latitude",
            "long",
            min_value=-32400000,
            max_value=32400000,
        ),
        FieldDefinition(
            "Boylam",
            "longitude",
            "long",
            min_value=-64800000,
            max_value=64800000,
        ),
        FieldDefinition(
            "Yükseklik",
            "altitude",
            "int",
            min_value=0,
            max_value=10000,
        ),
    ],
}


def get_message_type_label(message_id: int) -> str:
    """Return Turkish UI label for a message type."""
    labels = {1: "Mesaj 1 — Personel Bilgisi", 2: "Mesaj 2 — Birlik Konum Bilgisi"}
    return labels.get(message_id, f"Bilinmeyen Mesaj ({message_id})")


def get_message_short_label(message_id: int) -> str:
    """Return short log label for a message type."""
    return f"Mesaj {message_id}"


def message_to_dict(message: Message) -> dict[str, Any]:
    """Convert a message dataclass to a display-friendly dict."""
    if isinstance(message, Message1):
        return {
            "Mesaj ID": message.message_id,
            "Birlik Referans Numarası": message.unit_reference_no,
            "Adı": message.first_name,
            "Unit No": message.unit_no,
            "Soyadı": message.last_name,
            "Rütbe": f"{message.rank} — {RANK_LABELS.get(message.rank, '?')}",
        }
    return {
        "Mesaj ID": message.message_id,
        "Birlik Referans Numarası": message.unit_reference_no,
        "Birlik Konum Bilgisi Geçerliliği": (
            "Geçerli ✓" if message.position_validity else "Geçersiz ✗"
        ),
        "Enlem": message.latitude,
        "Boylam": message.longitude,
        "Yükseklik": message.altitude,
    }
