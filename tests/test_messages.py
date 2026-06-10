"""Tests for message metadata helpers."""

from src.protocol.messages import (
    MESSAGE_DEFINITIONS,
    Message1,
    Message2,
    field_range_hint,
    get_message_short_label,
    get_message_type_label,
    message_to_dict,
)


class TestMessageHelpers:
    def test_get_message_type_label(self):
        assert "Personnel" in get_message_type_label(1)
        assert "Position" in get_message_type_label(2)
        assert "Unknown" in get_message_type_label(99)

    def test_get_message_short_label(self):
        assert get_message_short_label(1) == "Message 1"

    def test_field_range_hint_fixed(self):
        field = MESSAGE_DEFINITIONS[1][0]
        assert "Fixed value: 1" in field_range_hint(field)

    def test_field_range_hint_string(self):
        field = MESSAGE_DEFINITIONS[1][2]
        assert "25 bytes" in field_range_hint(field)

    def test_field_range_hint_int_range(self):
        field = MESSAGE_DEFINITIONS[1][1]
        assert "-1000" in field_range_hint(field)

    def test_field_range_hint_bool(self):
        field = MESSAGE_DEFINITIONS[2][2]
        assert "Invalid" in field_range_hint(field)

    def test_message_to_dict_message1(self):
        msg = Message1(1, 100, "Ali", 42, "Yilmaz", 0)
        d = message_to_dict(msg)
        assert d["First Name"] == "Ali"
        assert "First Lieutenant" in d["Rank"]

    def test_message_to_dict_message2(self):
        msg = Message2(2, 2001, 1, 1, 2, 100)
        d = message_to_dict(msg)
        assert d["Position Valid"] == "Valid ✓"
        msg_invalid = Message2(2, 2001, 0, 1, 2, 100)
        assert message_to_dict(msg_invalid)["Position Valid"] == "Invalid ✗"
