"""Single application instance (server or client)."""

from __future__ import annotations

import queue
import uuid
from typing import Literal

from src.network.client import TcpClient
from src.network.handler import ConnectionHandler, NetworkEvent
from src.network.server import TcpServer
from src.protocol.messages import Message
from src.ui.main_view import InstancePanel

InstanceMode = Literal["server", "client"]


class Instance:
    """Manages one server or client instance with its own networking and UI panel."""

    def __init__(
        self,
        instance_id: str,
        mode: InstanceMode,
        panel: InstancePanel,
        event_queue: queue.Queue[NetworkEvent] | None = None,
    ) -> None:
        self.id = instance_id
        self.mode = mode
        self.panel = panel
        self.event_queue = event_queue or queue.Queue()
        self.port = 8080
        self.host = "127.0.0.1"

        self._server: TcpServer | None = None
        self._client: TcpClient | None = None
        self._handler: ConnectionHandler | None = None

        if mode == "server":
            self._server = TcpServer(self.event_queue)
            self._server.set_status_callback(self.panel.set_status)
            self._handler = self._server.handler
            self.panel.build_connection_controls(
                "server",
                on_start_server=self.start_server,
                on_stop_server=self.stop,
            )
            self.panel.set_send_callback(self.send_message)
            self.panel.set_send_raw_callback(self.send_raw)
            self.panel.set_connected_callback(
                lambda: self._server.is_connected if self._server else False
            )
            self.panel.set_listening_callback(
                lambda: self._server.is_running if self._server else False
            )
        else:
            self._client = TcpClient(self.event_queue)
            self._client.set_status_callback(self.panel.set_status)
            self._handler = self._client.handler
            self.panel.build_connection_controls(
                "client",
                on_connect=self.connect,
                on_disconnect=self.stop,
            )
            self.panel.set_send_callback(self.send_message)
            self.panel.set_send_raw_callback(self.send_raw)
            self.panel.set_connected_callback(
                lambda: self._client.is_connected if self._client else False
            )

        self.panel._auto_switch.configure(command=self._on_auto_toggle)  # noqa: SLF001
        if self._handler:
            self._handler.auto_response_enabled = self.panel.get_auto_response_enabled()

    @property
    def handler(self) -> ConnectionHandler | None:
        return self._handler

    @property
    def is_connected(self) -> bool:
        if self.mode == "server":
            return self._server.is_connected if self._server else False
        return self._client.is_connected if self._client else False

    @property
    def is_listening(self) -> bool:
        return self._server.is_running if self._server else False

    def set_title(self, title: str) -> None:
        self.panel.set_title(title)

    def start_server(self, port: int) -> bool:
        self.port = port
        if self._server and self._server.start(port):
            self.set_title(f"Server :{port}")
            return True
        return False

    def connect(self, host: str, port: int) -> bool:
        self.host = host
        self.port = port
        if self._client and self._client.connect(host, port):
            self.set_title(f"Client → {host}:{port}")
            return True
        return False

    def auto_connect(self, host: str = "127.0.0.1", port: int = 8080) -> bool:
        """Auto-start server or connect client based on mode."""
        if self.mode == "server":
            return self.start_server(port)
        return self.connect(host, port)

    def send_message(
        self, message: Message, is_auto: bool = False, is_periodic: bool = False
    ) -> bool:
        if self._handler:
            if not is_auto and not is_periodic:
                self._handler.auto_response_enabled = self.panel.get_auto_response_enabled()
            return self._handler.send_message(
                message, is_auto=is_auto, is_periodic=is_periodic
            )
        return False

    def send_raw(self, data: bytes) -> bool:
        if self._handler:
            return self._handler.send_raw(data)
        return False

    def process_events(self) -> None:
        """Drain event queue and update UI."""
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                self.panel.handle_network_event(event)
            except queue.Empty:
                break

    def stop(self) -> None:
        if self._server:
            self._server.stop()
        if self._client:
            self._client.disconnect()

    def _on_auto_toggle(self) -> None:
        if self._handler:
            self._handler.auto_response_enabled = self.panel.get_auto_response_enabled()

    @staticmethod
    def create_id() -> str:
        return str(uuid.uuid4())[:8]
