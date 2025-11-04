"""
Tests for logging module.
"""
import pytest
import logging
from logger import TradingLogger, get_logger
from pathlib import Path
import tempfile
import shutil


class TestTradingLogger:
    """Test logging functionality"""
    
    def setup_method(self):
        """Reset logger between tests"""
        TradingLogger._configured = False
        TradingLogger._loggers.clear()
        logging.getLogger().handlers.clear()
    
    def test_logger_setup(self):
        """Test basic logger setup"""
        TradingLogger.setup(log_level="INFO")
        assert TradingLogger._configured
    
    def test_get_logger(self):
        """Test getting a logger instance"""
        logger = TradingLogger.get_logger("test")
        assert logger is not None
        assert logger.name == "test"
    
    def test_get_logger_convenience(self):
        """Test convenience function"""
        logger = get_logger("test")
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_logger_with_file(self):
        """Test logger with file output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            TradingLogger.setup(log_level="DEBUG", log_dir=tmpdir)
            logger = TradingLogger.get_logger("test")
            logger.info("Test message")
            
            # Check log file was created
            log_files = list(Path(tmpdir).glob("*.log"))
            assert len(log_files) > 0
    
    def test_logger_levels(self):
        """Test different log levels"""
        TradingLogger.setup(log_level="WARNING")
        logger = TradingLogger.get_logger("test")
        
        # Should not raise errors
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
    
    def test_logger_auto_setup(self):
        """Test that logger sets up automatically"""
        # Don't call setup explicitly
        logger = get_logger("test")
        assert logger is not None
        assert TradingLogger._configured
    
    def test_logger_singleton(self):
        """Test that same logger name returns same instance"""
        logger1 = get_logger("test")
        logger2 = get_logger("test")
        assert logger1 is logger2

