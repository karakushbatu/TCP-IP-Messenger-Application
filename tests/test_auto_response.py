"""Tests for auto-response logic."""

from src.protocol.auto_response import (
    DEFAULT_MESSAGE_1,
    DEFAULT_MESSAGE_2,
    AutoResponseGuard,
    create_auto_response,
)
from src.protocol.messages import Message1, Message2


class TestCreateAutoResponse:
    def test_message1_triggers_message2(self):
        received = Message1(1, 100, "Test", 1, "User", 0)
        response = create_auto_response(received)
        assert isinstance(response, Message2)
        assert response.message_id == 2

    def test_message2_triggers_message1(self):
        received = Message2(2, 2001, 1, 100, 200, 500)
        response = create_auto_response(received)
        assert isinstance(response, Message1)
        assert response.message_id == 1


class TestAutoResponseGuard:
    def test_enabled_by_default(self):
        guard = AutoResponseGuard()
        msg = Message1(1, 100, "Test", 1, "User", 0)
        assert guard.should_auto_respond(msg) is True

    def test_disabled(self):
        guard = AutoResponseGuard(enabled=False)
        msg = Message1(1, 100, "Test", 1, "User", 0)
        assert guard.should_auto_respond(msg) is False

    def test_loop_prevention(self):
        guard = AutoResponseGuard()
        msg = Message1(1, 100, "Test", 1, "User", 0)
        assert guard.should_auto_respond(msg) is True
        guard.mark_auto_sent()
        assert guard.should_auto_respond(msg) is False

    def test_manual_send_resets_suppression(self):
        guard = AutoResponseGuard()
        msg = Message1(1, 100, "Test", 1, "User", 0)
        guard.mark_auto_sent()
        guard.mark_manual_sent()
        assert guard.should_auto_respond(msg) is True

    def test_default_payloads(self):
        assert DEFAULT_MESSAGE_1.message_id == 1
        assert DEFAULT_MESSAGE_2.message_id == 2
