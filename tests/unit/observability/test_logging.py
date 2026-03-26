"""Tests for structured logging configuration (Phase 8 - Red phase first)."""

from vectraxis.observability.logging import get_logger, setup_logging


class TestSetupLogging:
    def test_setup_logging_does_not_raise(self):
        setup_logging()

    def test_setup_logging_json_mode(self):
        setup_logging(log_level="DEBUG", json_output=True)


class TestGetLogger:
    def test_get_logger_returns_logger(self):
        setup_logging()
        logger = get_logger("test")
        assert logger is not None

    def test_logger_has_bind_method(self):
        setup_logging()
        logger = get_logger("test")
        assert hasattr(logger, "bind")
        bound = logger.bind(request_id="abc-123")
        assert bound is not None
