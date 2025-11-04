"""Type stubs for broker module"""
from typing import Dict, Optional, List
from config import Config

class Broker:
    config: Config
    paper_trading: bool
    api: Optional[any]
    
    def __init__(self, config: Optional[Config] = None, paper_trading: bool = True) -> None: ...
    
    def _connect(self) -> None: ...
    
    def get_account_info(self) -> Dict: ...
    
    def get_positions(self) -> List[Dict]: ...
    
    def get_current_price(self, symbol: str) -> float: ...
    
    def place_order(self, symbol: str, qty: int, side: str, 
                   order_type: str = 'market', time_in_force: str = 'day',
                   stop_loss: Optional[float] = None, 
                   take_profit: Optional[float] = None) -> Dict: ...
    
    def cancel_order(self, order_id: str) -> bool: ...
    
    def close_position(self, symbol: str) -> Dict: ...
    
    def is_market_open(self) -> bool: ...

