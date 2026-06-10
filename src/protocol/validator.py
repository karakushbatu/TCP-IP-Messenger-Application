"""Message field validation."""

from __future__ import annotations

from dataclasses import dataclass

from src.protocol.messages import (
    MESSAGE_DEFINITIONS,
    Message,
    Message1,
    Message2,
)


@dataclass
class ValidationError:
    field: str
    message: str
    min_value: int | None = None
    max_value: int | None = None


def _validate_int_field(
    field_name: str,
    value: object,
    min_value: int | None,
    max_value: int | None,
    ui_label: str,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(ValidationError(field_name, f"{ui_label} must be an integer."))
        return errors
    if min_value is not None and value < min_value:
        errors.append(
            ValidationError(
                field_name,
                f"{ui_label} must be at least {min_value}.",
                min_value=min_value,
                max_value=max_value,
            )
        )
    if max_value is not None and value > max_value:
        errors.append(
            ValidationError(
                field_name,
                f"{ui_label} must be at most {max_value}.",
                min_value=min_value,
                max_value=max_value,
            )
        )
    return errors


def _validate_string_field(
    field_name: str,
    value: object,
    byte_length: int,
    ui_label: str,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not isinstance(value, str):
        errors.append(ValidationError(field_name, f"{ui_label} must be text."))
        return errors
    encoded = value.encode("utf-8")
    if len(encoded) > byte_length:
        errors.append(
            ValidationError(
                field_name,
                f"{ui_label} must be at most {byte_length} bytes (currently {len(encoded)}).",
                max_value=byte_length,
            )
        )
    return errors


def validate_message1(data: dict[str, object]) -> list[ValidationError]:
    """Validate Message 1 field values."""
    errors: list[ValidationError] = []
    definitions = {f.internal_name: f for f in MESSAGE_DEFINITIONS[1]}

    msg_id = data.get("message_id", 1)
    if msg_id != 1:
        errors.append(
            ValidationError("message_id", "Message ID must be 1.", min_value=1, max_value=1)
        )

    for name in ("unit_reference_no", "unit_no", "rank"):
        field_def = definitions[name]
        errors.extend(
            _validate_int_field(
                name,
                data.get(name),
                field_def.min_value,
                field_def.max_value,
                field_def.ui_label,
            )
        )

    for name in ("first_name", "last_name"):
        field_def = definitions[name]
        errors.extend(
            _validate_string_field(
                name, data.get(name, ""), field_def.byte_length or 25, field_def.ui_label
            )
        )

    return errors


def validate_message2(data: dict[str, object]) -> list[ValidationError]:
    """Validate Message 2 field values."""
    errors: list[ValidationError] = []
    definitions = {f.internal_name: f for f in MESSAGE_DEFINITIONS[2]}

    msg_id = data.get("message_id", 2)
    if msg_id != 2:
        errors.append(
            ValidationError("message_id", "Message ID must be 2.", min_value=2, max_value=2)
        )

    for name in ("unit_reference_no", "position_validity", "latitude", "longitude", "altitude"):
        field_def = definitions[name]
        errors.extend(
            _validate_int_field(
                name,
                data.get(name),
                field_def.min_value,
                field_def.max_value,
                field_def.ui_label,
            )
        )

    return errors


def validate_message(message_id: int, data: dict[str, object]) -> list[ValidationError]:
    """Validate message fields by message type."""
    if message_id == 1:
        return validate_message1(data)
    if message_id == 2:
        return validate_message2(data)
    return [ValidationError("message_id", f"Invalid message type: {message_id}")]


def build_message(message_id: int, data: dict[str, object]) -> Message:
    """Build a validated message or raise ValueError."""
    errors = validate_message(message_id, data)
    if errors:
        raise ValueError(errors[0].message)

    if message_id == 1:
        return Message1(
            message_id=1,
            unit_reference_no=int(data["unit_reference_no"]),  # type: ignore[arg-type]
            first_name=str(data.get("first_name", "")),
            unit_no=int(data["unit_no"]),  # type: ignore[arg-type]
            last_name=str(data.get("last_name", "")),
            rank=int(data["rank"]),  # type: ignore[arg-type]
        )
    return Message2(
        message_id=2,
        unit_reference_no=int(data["unit_reference_no"]),  # type: ignore[arg-type]
        position_validity=int(data["position_validity"]),  # type: ignore[arg-type]
        latitude=int(data["latitude"]),  # type: ignore[arg-type]
        longitude=int(data["longitude"]),  # type: ignore[arg-type]
        altitude=int(data["altitude"]),  # type: ignore[arg-type]
    )
