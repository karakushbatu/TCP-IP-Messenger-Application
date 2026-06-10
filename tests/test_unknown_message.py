"""Tests for unknown message handling."""

import struct

import pytest

from src.protocol.errors import UnknownMessageError
from src.protocol.serializer import unpack_payload


class TestUnknownMessage:
    def test_unknown_id_99(self):
        payload = struct.pack("!i", 99) + b"\x00" * 25
        with pytest.raises(UnknownMessageError) as exc:
            unpack_payload(payload)
        assert exc.value.message_id == 99

    def test_unknown_id_0(self):
        payload = struct.pack("!i", 0) + b"\x00" * 25
        with pytest.raises(UnknownMessageError):
            unpack_payload(payload)
