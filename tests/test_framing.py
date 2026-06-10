"""Tests for TCP framing and partial reads."""

import socket
import struct
import threading

from src.protocol.messages import Message1
from src.protocol.serializer import (
    frame_payload,
    pack_message,
    read_exact,
    receive_framed_message,
    unpack_payload,
)


class TestReadExact:
    def test_read_exact_from_socket(self):
        server_sock, client_sock = socket.socketpair()
        payload = pack_message(
            Message1(1, 100, "Test", 1, "User", 0)
        )
        framed = frame_payload(payload)
        client_sock.sendall(framed)

        received_payload = receive_framed_message(server_sock)
        assert unpack_payload(received_payload) == unpack_payload(payload)

        server_sock.close()
        client_sock.close()

    def test_partial_reads(self):
        server_sock, client_sock = socket.socketpair()
        data = b"hello world"

        def sender():
            for byte in data:
                client_sock.send(bytes([byte]))

        thread = threading.Thread(target=sender)
        thread.start()
        result = read_exact(server_sock, len(data))
        thread.join()
        assert result == data
        server_sock.close()
        client_sock.close()

    def test_length_header(self):
        payload = b"\x01\x02\x03\x04"
        framed = frame_payload(payload)
        length = struct.unpack("!I", framed[:4])[0]
        assert length == 4
        assert framed[4:] == payload
