"""Shared test fixtures."""

import pytest

from src.protocol.auto_response import DEFAULT_MESSAGE_1, DEFAULT_MESSAGE_2


@pytest.fixture
def sample_message1():
    return DEFAULT_MESSAGE_1


@pytest.fixture
def sample_message2():
    return DEFAULT_MESSAGE_2
