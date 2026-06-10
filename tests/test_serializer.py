"""Tests for binary serialization."""

import struct

import pytest

from src.protocol.errors import ProtocolError, UnknownMessageError
from src.protocol.messages import MESSAGE_1_SIZE, MESSAGE_2_SIZE, Message1
from src.protocol.serializer import (
    decode_fixed_string,
    encode_fixed_string,
    frame_payload,
    pack_message,
    unpack_payload,
)


class TestFixedString:
    def test_encode_decode_roundtrip(self):
        encoded = encode_fixed_string("Ali")
        assert len(encoded) == 25
        assert decode_fixed_string(encoded) == "Ali"

    def test_null_padding(self):
        encoded = encode_fixed_string("A")
        assert encoded.endswith(b"\x00" * 24)

    def test_turkish_characters(self):
        for char in ["ğ", "ş", "ö", "ü", "ç", "ı"]:
            encoded = encode_fixed_string(char)
            assert decode_fixed_string(encoded) == char

    def test_reject_long_string(self):
        with pytest.raises(ValueError):
            encode_fixed_string("a" * 26)


class TestMessage1Serialization:
    def test_pack_size(self, sample_message1):
        payload = pack_message(sample_message1)
        assert len(payload) == MESSAGE_1_SIZE

    def test_roundtrip(self, sample_message1):
        payload = pack_message(sample_message1)
        result = unpack_payload(payload)
        assert result == sample_message1

    def test_turkish_name_roundtrip(self):
        msg = Message1(1, 100, "Öğür", 1, "Şahin", 1)
        result = unpack_payload(pack_message(msg))
        assert result.first_name == "Öğür"
        assert result.last_name == "Şahin"


class TestMessage2Serialization:
    def test_pack_size(self, sample_message2):
        payload = pack_message(sample_message2)
        assert len(payload) == MESSAGE_2_SIZE

    def test_roundtrip(self, sample_message2):
        payload = pack_message(sample_message2)
        result = unpack_payload(payload)
        assert result == sample_message2


class TestFraming:
    def test_frame_payload(self, sample_message1):
        payload = pack_message(sample_message1)
        framed = frame_payload(payload)
        header = struct.unpack("!I", framed[:4])[0]
        assert header == len(payload)
        assert framed[4:] == payload


class TestUnpackErrors:
    def test_unknown_message_id(self):
        payload = struct.pack("!i", 99) + b"\x00" * 20
        with pytest.raises(UnknownMessageError) as exc:
            unpack_payload(payload)
        assert exc.value.message_id == 99

    def test_truncated_message1(self):
        payload = struct.pack("!i", 1) + b"\x00" * 10
        with pytest.raises(ProtocolError):
            unpack_payload(payload)

    def test_truncated_message2(self):
        payload = struct.pack("!i", 2) + b"\x00" * 5
        with pytest.raises(ProtocolError):
            unpack_payload(payload)
