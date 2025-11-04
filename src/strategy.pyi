"""Type stubs for strategy module"""
import pandas as pd
from typing import Dict, Optional, Any
from config import Config

class TradingStrategy:
    config: Config
    
    def __init__(self, config: Optional[Config] = None) -> None: ...
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame: ...
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame: ...
    
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame: ...
    
    def get_current_signal(self, df: pd.DataFrame) -> Dict[str, Any]: ...

