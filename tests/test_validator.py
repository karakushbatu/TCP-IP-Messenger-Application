"""Tests for message validation."""

import pytest

from src.protocol.validator import (
    build_message,
    validate_message,
    validate_message1,
)


class TestMessage1Validation:
    def test_valid_message(self):
        data = {
            "message_id": 1,
            "unit_reference_no": 100,
            "first_name": "Ali",
            "unit_no": 42,
            "last_name": "Yılmaz",
            "rank": 0,
        }
        errors = validate_message1(data)
        assert errors == []

    def test_unit_reference_out_of_range(self):
        data = {
            "message_id": 1,
            "unit_reference_no": 10000,
            "first_name": "Ali",
            "unit_no": 42,
            "last_name": "Yılmaz",
            "rank": 0,
        }
        errors = validate_message1(data)
        assert any(e.field == "unit_reference_no" for e in errors)

    def test_string_too_long_bytes(self):
        data = {
            "message_id": 1,
            "unit_reference_no": 100,
            "first_name": "ğ" * 26,
            "unit_no": 42,
            "last_name": "Yılmaz",
            "rank": 0,
        }
        errors = validate_message1(data)
        assert any(e.field == "first_name" for e in errors)

    def test_boundary_min(self):
        data = {
            "message_id": 1,
            "unit_reference_no": -1000,
            "first_name": "",
            "unit_no": 0,
            "last_name": "",
            "rank": 0,
        }
        assert validate_message1(data) == []

    def test_boundary_max(self):
        data = {
            "message_id": 1,
            "unit_reference_no": 9999,
            "first_name": "A",
            "unit_no": 4294967295,
            "last_name": "B",
            "rank": 2,
        }
        assert validate_message1(data) == []

    def test_boundary_min_minus_one(self):
        data = {
            "message_id": 1,
            "unit_reference_no": -1001,
            "first_name": "A",
            "unit_no": 0,
            "last_name": "B",
            "rank": 0,
        }
        errors = validate_message1(data)
        assert len(errors) > 0


class TestMessage2Validation:
    def test_valid_message(self):
        data = {
            "message_id": 2,
            "unit_reference_no": 2001,
            "position_validity": 1,
            "latitude": 23456789,
            "longitude": 17654321,
            "altitude": 1500,
        }
        assert validate_message(2, data) == []

    def test_unit_reference_min_zero_invalid(self):
        data = {
            "message_id": 2,
            "unit_reference_no": 0,
            "position_validity": 1,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0,
        }
        errors = validate_message(2, data)
        assert any(e.field == "unit_reference_no" for e in errors)

    def test_altitude_max_plus_one(self):
        data = {
            "message_id": 2,
            "unit_reference_no": 1,
            "position_validity": 1,
            "latitude": 0,
            "longitude": 0,
            "altitude": 10001,
        }
        errors = validate_message(2, data)
        assert any(e.field == "altitude" for e in errors)


class TestBuildMessage:
    def test_build_message1(self):
        data = {
            "message_id": 1,
            "unit_reference_no": 100,
            "first_name": "Ali",
            "unit_no": 42,
            "last_name": "Yılmaz",
            "rank": 1,
        }
        msg = build_message(1, data)
        assert msg.message_id == 1
        assert msg.first_name == "Ali"

    def test_build_invalid_raises(self):
        with pytest.raises(ValueError):
            build_message(1, {"message_id": 1, "unit_reference_no": 99999})
