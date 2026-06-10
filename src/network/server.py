"""TCP server implementation."""

from __future__ import annotations

import queue
import socket
import threading
from typing import Callable

from src.network.handler import ConnectionHandler, NetworkEvent


class TcpServer:
    """TCP server that accepts one active connection at a time."""

    def __init__(self, event_queue: queue.Queue[NetworkEvent]) -> None:
        self._event_queue = event_queue
        self._handler = ConnectionHandler(event_queue)
        self._server_socket: socket.socket | None = None
        self._accept_thread: threading.Thread | None = None
        self._running = False
        self._port = 0
        self._status_callback: Callable[[str], None] | None = None

    @property
    def handler(self) -> ConnectionHandler:
        return self._handler

    @property
    def port(self) -> int:
        return self._port

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_connected(self) -> bool:
        return self._handler.is_connected

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        self._status_callback = callback

    def _set_status(self, status: str) -> None:
        if self._status_callback:
            self._status_callback(status)

    def start(self, port: int) -> bool:
        """Start listening on the given port."""
        self.stop()
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", port))
            self._server_socket.listen(1)
            self._port = port
            self._running = True
            self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._accept_thread.start()
            self._set_status("Bağlantı bekleniyor...")
            return True
        except OSError:
            self.stop()
            return False

    def stop(self) -> None:
        """Stop server and close connections."""
        self._running = False
        self._handler.close()
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None
        self._set_status("Bağlantı yok")

    def _accept_loop(self) -> None:
        while self._running and self._server_socket:
            try:
                client_sock, _addr = self._server_socket.accept()
                self._handler.close()
                self._handler.set_socket(client_sock)
                self._set_status("Bağlı")
            except OSError:
                break
