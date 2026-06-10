"""TCP client implementation."""

from __future__ import annotations

import queue
import socket
from typing import Callable

from src.network.handler import ConnectionHandler, NetworkEvent


class TcpClient:
    """TCP client that connects to a remote server."""

    def __init__(self, event_queue: queue.Queue[NetworkEvent]) -> None:
        self._event_queue = event_queue
        self._handler = ConnectionHandler(event_queue)
        self._status_callback: Callable[[str], None] | None = None

    @property
    def handler(self) -> ConnectionHandler:
        return self._handler

    @property
    def is_connected(self) -> bool:
        return self._handler.is_connected

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        self._status_callback = callback

    def _set_status(self, status: str) -> None:
        if self._status_callback:
            self._status_callback(status)

    def connect(self, host: str, port: int) -> bool:
        """Connect to a remote server."""
        self.disconnect()
        self._set_status("Connecting...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # fail fast if host/port unreachable
            sock.connect((host, port))
            sock.settimeout(None)  # blocking reads in receive loop
            self._handler.set_socket(sock)
            self._set_status("Connected")
            return True
        except OSError:
            self._set_status("Not connected")
            return False

    def disconnect(self) -> None:
        """Disconnect from server."""
        self._handler.close()
        self._set_status("Not connected")
