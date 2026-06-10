"""Auto-response message generation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from src.protocol.messages import Message, Message1, Message2

DEFAULT_MESSAGE_1 = Message1(
    message_id=1,
    unit_reference_no=1001,
    first_name="Ali",
    unit_no=42,
    last_name="Yılmaz",
    rank=0,
)

DEFAULT_MESSAGE_2 = Message2(
    message_id=2,
    unit_reference_no=2001,
    position_validity=1,
    latitude=23456789,
    longitude=17654321,
    altitude=1500,
)


def create_auto_response(received: Message) -> Message | None:
    """Create the appropriate auto-response for a received message."""
    if isinstance(received, Message1):
        return DEFAULT_MESSAGE_2
    if isinstance(received, Message2):
        return DEFAULT_MESSAGE_1
    return None


@dataclass
class AutoResponseGuard:
    """Prevents infinite auto-response ping-pong loops."""

    enabled: bool = True
    prevent_loop: bool = True
    suppression_window_ms: float = 500.0
    _last_auto_send_time: float = field(default=0.0, repr=False)
    _suppress_next: bool = field(default=False, repr=False)

    def should_auto_respond(self, received: Message, is_auto_tagged: bool = False) -> bool:
        """Determine whether an auto-response should be sent."""
        if not self.enabled:
            return False
        if is_auto_tagged:
            return False
        if self.prevent_loop and self._suppress_next:
            self._suppress_next = False
            return False  # skip one hop to break A→B→A→B ping-pong
        return create_auto_response(received) is not None

    def mark_auto_sent(self) -> None:
        """Record that an auto-response was just sent."""
        self._last_auto_send_time = time.monotonic() * 1000
        self._suppress_next = True

    def mark_manual_sent(self) -> None:
        """Record that a manual message was sent (resets suppression)."""
        self._suppress_next = False

    def check_suppression_window(self) -> bool:
        """Return True if still within suppression window after auto-send."""
        if not self.prevent_loop:
            return False
        elapsed = time.monotonic() * 1000 - self._last_auto_send_time
        return elapsed < self.suppression_window_ms
