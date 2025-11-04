"""Type stubs for logger module"""
import logging
from typing import Optional, Dict

class TradingLogger:
    _loggers: Dict[str, logging.Logger]
    _configured: bool
    
    @classmethod
    def setup(cls, log_level: str = "INFO", log_dir: Optional[str] = None) -> None: ...
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger: ...

def get_logger(name: str) -> logging.Logger: ...

