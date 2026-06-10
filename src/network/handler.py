"""Shared network event types and connection handler."""

from __future__ import annotations

import queue
import socket
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from src.protocol.auto_response import AutoResponseGuard, create_auto_response
from src.protocol.errors import ProtocolError, UnknownMessageError
from src.protocol.messages import Message
from src.protocol.serializer import (
    frame_payload,
    pack_message,
    receive_framed_message,
    unpack_payload,
)

EventType = Literal[
    "connected",
    "disconnected",
    "message_received",
    "message_sent",
    "unknown_message",
    "protocol_error",
    "error",
]


@dataclass
class NetworkEvent:
    type: EventType
    payload: object | None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SentMessageInfo:
    message: Message
    is_auto: bool = False
    is_periodic: bool = False


@dataclass
class ReceivedMessageInfo:
    message: Message | None
    is_auto: bool = False
    raw_error: str | None = None
    unknown_id: int | None = None


class ConnectionHandler:
    """Manages send/receive on a single TCP connection."""

    def __init__(self, event_queue: queue.Queue[NetworkEvent]) -> None:
        self._event_queue = event_queue  # thread-safe bridge to UI main thread
        self._socket: socket.socket | None = None
        self._lock = threading.Lock()
        self._running = False
        self._recv_thread: threading.Thread | None = None
        self.auto_response_guard = AutoResponseGuard()
        self.auto_response_enabled = True

    @property
    def is_connected(self) -> bool:
        return self._socket is not None and self._running

    def set_socket(self, sock: socket.socket | None) -> None:
        """Attach a socket and start the receive loop."""
        self.close()
        if sock is None:
            return
        self._socket = sock
        self._running = True
        self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._recv_thread.start()
        self._emit("connected", None)  # UI polls queue, never touches socket directly

    def close(self) -> None:
        """Close connection and stop receive thread."""
        was_connected = self._socket is not None
        self._running = False
        with self._lock:
            if self._socket:
                try:
                    self._socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    self._socket.close()
                except OSError:
                    pass
                self._socket = None
        if was_connected:
            self._emit("disconnected", None)

    def send_message(
        self, message: Message, is_auto: bool = False, is_periodic: bool = False
    ) -> bool:
        """Send a framed message over the connection."""
        with self._lock:
            if not self._socket or not self._running:
                return False
            try:
                payload = pack_message(message)
                framed = frame_payload(payload)
                self._socket.sendall(framed)
                if is_auto:
                    self.auto_response_guard.mark_auto_sent()
                else:
                    self.auto_response_guard.mark_manual_sent()  # manual send resets loop guard
                self._emit(
                    "message_sent",
                    SentMessageInfo(message=message, is_auto=is_auto, is_periodic=is_periodic),
                )
                return True
            except OSError as exc:
                self._emit("error", str(exc))
                self.close()
                return False

    def send_raw(self, data: bytes) -> bool:
        """Send raw bytes (for test helpers)."""
        with self._lock:
            if not self._socket or not self._running:
                return False
            try:
                self._socket.sendall(data)
                return True
            except OSError as exc:
                self._emit("error", str(exc))
                self.close()
                return False

    def _emit(self, event_type: EventType, payload: object | None) -> None:
        self._event_queue.put(NetworkEvent(type=event_type, payload=payload))

    def _receive_loop(self) -> None:
        while self._running:
            sock = self._socket
            if sock is None:
                break
            try:
                payload = receive_framed_message(sock)
                try:
                    message = unpack_payload(payload)
                    self._emit(
                        "message_received",
                        ReceivedMessageInfo(message=message, is_auto=False),
                    )
                    self._handle_auto_response(message)
                except UnknownMessageError as exc:
                    self._emit(
                        "unknown_message",
                        ReceivedMessageInfo(
                            message=None,
                            unknown_id=exc.message_id,
                            raw_error=str(exc),
                        ),
                    )
                except ProtocolError as exc:
                    self._emit(
                        "protocol_error",
                        ReceivedMessageInfo(message=None, raw_error=str(exc)),
                    )
            except ConnectionError:
                break
            except OSError:
                break
        if self._running:
            self.close()

    def _handle_auto_response(self, received: Message) -> None:
        if not self.auto_response_enabled:
            return
        if not self.auto_response_guard.should_auto_respond(received):
            return
        response = create_auto_response(received)
        if response:
            self.send_message(response, is_auto=True)
