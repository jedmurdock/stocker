"""Type stubs for backtester module"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
from strategy import TradingStrategy
from data_fetcher import DataFetcher
from config import Config

class Backtester:
    initial_capital: float
    config: Config
    strategy: TradingStrategy
    data_fetcher: DataFetcher
    
    def __init__(self, initial_capital: float = 10000, config: Optional[Config] = None) -> None: ...
    
    def run_backtest(self, symbol: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> Dict: ...
    
    def _simulate_trades(self, df: pd.DataFrame) -> Tuple[List[Dict], pd.Series]: ...
    
    def _calculate_metrics(self, trades: List[Dict], portfolio_value: pd.Series, 
                          df: pd.DataFrame) -> Dict: ...

