"""Integration tests for TCP server/client communication."""

import queue
import socket
import struct
import time

from src.network.client import TcpClient
from src.network.handler import ReceivedMessageInfo
from src.network.server import TcpServer
from src.protocol.messages import Message1
from src.protocol.serializer import frame_payload


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestServerClientIntegration:
    def test_connect_and_send_message1(self):
        port = _find_free_port()
        server_queue: queue.Queue = queue.Queue()
        client_queue: queue.Queue = queue.Queue()

        server = TcpServer(server_queue)
        client = TcpClient(client_queue)
        server.handler.auto_response_enabled = False
        client.handler.auto_response_enabled = False

        assert server.start(port)
        time.sleep(0.1)
        assert client.connect("127.0.0.1", port)
        time.sleep(0.2)

        msg = Message1(1, 500, "Test", 10, "Kullanıcı", 1)
        assert client.handler.send_message(msg)

        time.sleep(0.3)

        received = False
        while not server_queue.empty():
            event = server_queue.get_nowait()
            if event.type == "message_received":
                info = event.payload
                if isinstance(info, ReceivedMessageInfo) and info.message:
                    assert info.message.first_name == "Test"
                    received = True

        assert received
        server.stop()
        client.disconnect()

    def test_auto_response_message1_to_message2(self):
        port = _find_free_port()
        server_queue: queue.Queue = queue.Queue()
        client_queue: queue.Queue = queue.Queue()

        server = TcpServer(server_queue)
        client = TcpClient(client_queue)
        server.handler.auto_response_enabled = True
        client.handler.auto_response_enabled = False

        assert server.start(port)
        time.sleep(0.1)
        assert client.connect("127.0.0.1", port)
        time.sleep(0.2)

        msg = Message1(1, 500, "Test", 10, "Kullanıcı", 1)
        client.handler.send_message(msg)
        time.sleep(0.5)

        got_msg2 = False
        while not client_queue.empty():
            event = client_queue.get_nowait()
            if event.type == "message_received":
                info = event.payload
                if isinstance(info, ReceivedMessageInfo) and info.message:
                    if info.message.message_id == 2:
                        got_msg2 = True

        assert got_msg2
        server.stop()
        client.disconnect()

    def test_unknown_message_event(self):
        port = _find_free_port()
        server_queue: queue.Queue = queue.Queue()
        client_queue: queue.Queue = queue.Queue()

        server = TcpServer(server_queue)
        client = TcpClient(client_queue)

        assert server.start(port)
        time.sleep(0.1)
        assert client.connect("127.0.0.1", port)
        time.sleep(0.2)

        payload = struct.pack("!i", 99)
        framed = frame_payload(payload)
        client.handler.send_raw(framed)
        time.sleep(0.3)

        got_unknown = False
        while not server_queue.empty():
            event = server_queue.get_nowait()
            if event.type == "unknown_message":
                got_unknown = True

        assert got_unknown
        server.stop()
        client.disconnect()

    def test_disconnect_event(self):
        port = _find_free_port()
        server_queue: queue.Queue = queue.Queue()
        client_queue: queue.Queue = queue.Queue()

        server = TcpServer(server_queue)
        client = TcpClient(client_queue)

        assert server.start(port)
        time.sleep(0.1)
        assert client.connect("127.0.0.1", port)
        time.sleep(0.1)

        client.disconnect()
        time.sleep(0.3)

        got_disconnect = False
        while not server_queue.empty():
            event = server_queue.get_nowait()
            if event.type == "disconnected":
                got_disconnect = True

        assert got_disconnect
        server.stop()
