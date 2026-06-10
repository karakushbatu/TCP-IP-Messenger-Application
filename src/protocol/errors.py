"""Protocol-level exceptions."""


class ProtocolError(Exception):
    """Raised when payload is corrupt or truncated."""


class UnknownMessageError(Exception):
    """Raised when message ID is not recognized."""

    def __init__(self, message_id: int) -> None:
        self.message_id = message_id
        super().__init__(f"Unknown message ID: {message_id}")
