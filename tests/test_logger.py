import pytest
from src.logger import get_logger, init_logger

def test_logger(capsys, monkeypatch):
    from src import logger
    # Reset singleton to force re-initialization if needed
    monkeypatch.setattr(logger, "singleton", None)
    l = logger.get_logger()
    
    # Test fallback to print when no logger is set
    l.info("info message")
    captured = capsys.readouterr()
    assert "INFO: info message" in captured.out
    
    l.error("error message")
    captured = capsys.readouterr()
    assert "ERROR: error message" in captured.out
    
    l.debug("debug message")
    captured = capsys.readouterr()
    assert "DEBUG: debug message" in captured.out
    
    l.warning("warning message")
    captured = capsys.readouterr()
    assert "WARNING: warning message" in captured.out

def test_logger_with_flask_logger(app):
    init_logger(app.logger)
    logger = get_logger()
    
    # These should now use app.logger instead of print
    # We just check they don't crash and maybe check logs if possible
    logger.info("flask info")
    logger.error("flask error")
    logger.debug("flask debug")
    logger.warning("flask warning")
