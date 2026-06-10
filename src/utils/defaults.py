"""Default form values for quick fill."""

from src.protocol.auto_response import DEFAULT_MESSAGE_1, DEFAULT_MESSAGE_2

QUICK_FILL_MESSAGE_1: dict[str, object] = {
    "message_id": DEFAULT_MESSAGE_1.message_id,
    "unit_reference_no": DEFAULT_MESSAGE_1.unit_reference_no,
    "first_name": DEFAULT_MESSAGE_1.first_name,
    "unit_no": DEFAULT_MESSAGE_1.unit_no,
    "last_name": DEFAULT_MESSAGE_1.last_name,
    "rank": DEFAULT_MESSAGE_1.rank,
}

QUICK_FILL_MESSAGE_2: dict[str, object] = {
    "message_id": DEFAULT_MESSAGE_2.message_id,
    "unit_reference_no": DEFAULT_MESSAGE_2.unit_reference_no,
    "position_validity": DEFAULT_MESSAGE_2.position_validity,
    "latitude": DEFAULT_MESSAGE_2.latitude,
    "longitude": DEFAULT_MESSAGE_2.longitude,
    "altitude": DEFAULT_MESSAGE_2.altitude,
}
