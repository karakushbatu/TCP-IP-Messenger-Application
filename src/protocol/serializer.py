"""Binary serialization and TCP framing helpers."""

from __future__ import annotations

import socket
import struct

from src.protocol.errors import ProtocolError, UnknownMessageError
from src.protocol.messages import (
    MESSAGE_1_FORMAT,
    MESSAGE_1_SIZE,
    MESSAGE_2_FORMAT,
    MESSAGE_2_SIZE,
    Message,
    Message1,
    Message2,
)

HEADER_FORMAT = "!I"  # 4-byte big-endian length prefix before every payload
HEADER_SIZE = 4


def encode_fixed_string(value: str, size: int = 25) -> bytes:
    """Encode a UTF-8 string to a fixed-size null-padded byte field."""
    encoded = value.encode("utf-8")
    if len(encoded) > size:
        raise ValueError(f"String exceeds {size} bytes")
    return encoded.ljust(size, b"\x00")


def decode_fixed_string(value: bytes) -> str:
    """Decode a fixed-size null-padded byte field to UTF-8 string."""
    return value.rstrip(b"\x00").decode("utf-8")


def pack_message(message: Message) -> bytes:
    """Pack a message dataclass into binary payload bytes."""
    if isinstance(message, Message1):
        return struct.pack(
            MESSAGE_1_FORMAT,
            message.message_id,
            message.unit_reference_no,
            encode_fixed_string(message.first_name),
            message.unit_no,
            encode_fixed_string(message.last_name),
            message.rank,
        )
    return struct.pack(
        MESSAGE_2_FORMAT,
        message.message_id,
        message.unit_reference_no,
        message.position_validity,
        message.latitude,
        message.longitude,
        message.altitude,
    )


def unpack_payload(payload: bytes) -> Message:
    """Unpack binary payload bytes into a message dataclass."""
    if len(payload) < 4:
        raise ProtocolError("Payload too short to read message ID")

    message_id = struct.unpack("!i", payload[:4])[0]

    if message_id == 1:
        if len(payload) < MESSAGE_1_SIZE:
            raise ProtocolError(f"Message 1 payload truncated: expected {MESSAGE_1_SIZE} bytes")
        fields = struct.unpack(MESSAGE_1_FORMAT, payload[:MESSAGE_1_SIZE])
        return Message1(
            message_id=fields[0],
            unit_reference_no=fields[1],
            first_name=decode_fixed_string(fields[2]),
            unit_no=fields[3],
            last_name=decode_fixed_string(fields[4]),
            rank=fields[5],
        )

    if message_id == 2:
        if len(payload) < MESSAGE_2_SIZE:
            raise ProtocolError(f"Message 2 payload truncated: expected {MESSAGE_2_SIZE} bytes")
        fields = struct.unpack(MESSAGE_2_FORMAT, payload[:MESSAGE_2_SIZE])
        return Message2(
            message_id=fields[0],
            unit_reference_no=fields[1],
            position_validity=fields[2],
            latitude=fields[3],
            longitude=fields[4],
            altitude=fields[5],
        )

    raise UnknownMessageError(message_id)


def frame_payload(payload: bytes) -> bytes:
    """Add 4-byte length header before payload."""
    return struct.pack(HEADER_FORMAT, len(payload)) + payload


def read_exact(sock: socket.socket, size: int) -> bytes:
    """Read exactly `size` bytes from socket, handling partial reads."""
    # TCP is a stream — recv() may return fewer bytes than requested
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("Socket connection closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def receive_framed_message(sock: socket.socket) -> bytes:
    """Receive a length-prefixed framed message payload."""
    header = read_exact(sock, HEADER_SIZE)
    payload_length = struct.unpack(HEADER_FORMAT, header)[0]
    if payload_length == 0:
        raise ProtocolError("Empty payload length")
    return read_exact(sock, payload_length)
