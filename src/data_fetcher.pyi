"""Type stubs for data_fetcher module"""
import pandas as pd
from typing import Optional
from config import Config

class DataFetcher:
    source: str
    config: Config
    
    def __init__(self, source: str = 'yfinance') -> None: ...
    
    def fetch_data(self, symbol: str, period: Optional[int] = None) -> pd.DataFrame: ...
    
    def _fetch_yfinance(self, symbol: str, period: int) -> pd.DataFrame: ...
    
    def _fetch_alpaca(self, symbol: str, period: int) -> pd.DataFrame: ...
    
    def get_current_price(self, symbol: str) -> float: ...

