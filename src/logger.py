"""
Structured logging configuration for the trading system.
Provides consistent logging across all modules.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class TradingLogger:
    """
    Centralized logging configuration for the trading system.
    Supports both file and console output with structured formatting.
    """
    
    _loggers = {}
    _configured = False
    
    @classmethod
    def setup(cls, log_level: str = "INFO", log_dir: Optional[str] = None):
        """
        Set up logging configuration for the entire application.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files. If None, only console logging.
        """
        if cls._configured:
            return
        
        # Create log directory if specified
        if log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)
            
            # Create log file with timestamp
            log_file = log_path / f"trading_{datetime.now().strftime('%Y%m%d')}.log"
        else:
            log_file = None
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler (less verbose)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (more detailed)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (typically __name__ of the module)
            
        Returns:
            Logger instance
        """
        if not cls._configured:
            cls.setup()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Logger name (use __name__)
        
    Returns:
        Logger instance
    """
    return TradingLogger.get_logger(name)

