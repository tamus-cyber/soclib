"""Test VectraClient logging"""
import os
from loguru import logger
from azure.identity import DefaultAzureCredential
from ... import vectra
from ...vectra import VectraClient

BASE_URL = os.getenv('VECTRA_API_URL')


class LogSink:  # pylint: disable=too-few-public-methods
    """Log sink for testing
    Any object with a write method can be used as a log sink in loguru,
    so making this simple class allows us to capture log messages in a list.
    """
    def __init__(self):
        self.messages = []

    def write(self, message):
        """loguru will call this method to write a message to the sink whenever a message is logged"""
        self.messages.append(message)

class TestVectraClientLogging:
    """Test VectraClient logging."""
    def test_logging_is_disabled_by_default(self):
        """Test that logging is disabled by default."""

        # Set up logging sink so we can check if a message is logged
        log_sink = LogSink()
        logger.add(log_sink, format="{level}", level="DEBUG")

        # Creating a VectraClient will log a debug message if logging is enabled
        _ = VectraClient(BASE_URL, DefaultAzureCredential())

        # Check that the message was not logged
        assert not log_sink.messages # nosec B101

    def test_logging_can_be_enabled(self):
        """Test that logging can be enabled."""

        # Set up logging sink so we can check if a message is logged
        log_sink = LogSink()
        logger.add(log_sink, format="{level}", level="DEBUG")

        logger.enable(vectra.__name__)

        # Creating a VectraClient will log a debug message if logging is enabled
        _ = VectraClient(BASE_URL, DefaultAzureCredential())

        # Check that the message was logged
        assert log_sink.messages # nosec B101

        # Check that the message was logged at the correct level
        assert log_sink.messages[0].strip() == "DEBUG" # nosec B101
