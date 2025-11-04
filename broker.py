"""
Broker integration module for executing real trades.
Currently supports Alpaca API for paper and live trading.
"""
from typing import Dict, Optional, List
from datetime import datetime
from config import Config


class Broker:
    """
    Broker interface for executing trades.
    Supports Alpaca API for paper and live trading.
    """
    
    def __init__(self, config: Optional[Config] = None, paper_trading: bool = True):
        """
        Initialize broker connection.
        
        Args:
            config: Configuration object
            paper_trading: If True, use paper trading account
        """
        self.config = config or Config()
        self.paper_trading = paper_trading
        self.api = None
        self._connect()
    
    def _connect(self):
        """Establish connection to broker API"""
        # Validate credentials
        if not self.config.ALPACA_API_KEY or not self.config.ALPACA_SECRET_KEY:
            raise ValueError(
                "Alpaca API credentials not configured. "
                "Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file."
            )
        
        try:
            import alpaca_trade_api as tradeapi
            
            if self.paper_trading:
                base_url = 'https://paper-api.alpaca.markets'
            else:
                base_url = 'https://api.alpaca.markets'
            
            self.api = tradeapi.REST(
                self.config.ALPACA_API_KEY,
                self.config.ALPACA_SECRET_KEY,
                base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.api.get_account()
            print(f"Connected to Alpaca ({'Paper' if self.paper_trading else 'Live'} Trading)")
            print(f"Account Status: {account.status}")
            print(f"Buying Power: ${float(account.buying_power):,.2f}")
            
        except ImportError:
            raise ImportError("alpaca-trade-api not installed. Install with: pip install alpaca-trade-api")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to broker: {e}")
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        account = self.api.get_account()
        return {
            'status': account.status,
            'buying_power': float(account.buying_power),
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),
            'equity': float(account.equity),
            'day_trading_buying_power': float(account.daytrading_buying_power)
        }
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        positions = self.api.list_positions()
        return [{
            'symbol': pos.symbol,
            'qty': int(pos.qty),
            'avg_entry_price': float(pos.avg_entry_price),
            'current_price': float(pos.current_price),
            'market_value': float(pos.market_value),
            'unrealized_pl': float(pos.unrealized_pl),
            'side': pos.side
        } for pos in positions]
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        try:
            quote = self.api.get_latest_quote(symbol)
            return float(quote.bp)  # Use bid price
        except Exception as e:
            # Fallback to last trade price
            try:
                trade = self.api.get_latest_trade(symbol)
                return float(trade.price)
            except Exception as trade_error:
                raise RuntimeError(f"Failed to get current price for {symbol}: {trade_error}")
    
    def place_order(self, symbol: str, qty: int, side: str, 
                   order_type: str = 'market', time_in_force: str = 'day',
                   stop_loss: Optional[float] = None, 
                   take_profit: Optional[float] = None) -> Dict:
        """
        Place an order.
        
        Args:
            symbol: Stock ticker
            qty: Number of shares (positive integer)
            side: 'buy' or 'sell'
            order_type: 'market', 'limit', etc.
            time_in_force: 'day', 'gtc', etc.
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            
        Returns:
            Order information dictionary
            
        Raises:
            ValueError: If side is invalid or qty is not positive
            RuntimeError: If not connected or order fails
        """
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        if side not in ['buy', 'sell']:
            raise ValueError("side must be 'buy' or 'sell'")
        
        if qty <= 0:
            raise ValueError(f"qty must be positive, got: {qty}")
        
        try:
            # Place main order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
            
            result = {
                'order_id': order.id,
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'status': order.status,
                'submitted_at': order.submitted_at
            }
            
            # Note: Alpaca doesn't support stop-loss/take-profit as part of order
            # These would need to be tracked separately and managed manually
            if stop_loss or take_profit:
                result['warning'] = 'Stop-loss and take-profit must be managed separately'
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to place order: {e}")
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        try:
            self.api.cancel_order(order_id)
            return True
        except Exception as e:
            print(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def close_position(self, symbol: str) -> Dict:
        """Close an existing position"""
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        try:
            position = self.api.get_position(symbol)
            qty = abs(int(position.qty))
            side = 'sell' if int(position.qty) > 0 else 'buy'
            
            return self.place_order(symbol, qty, side)
        except Exception as e:
            raise RuntimeError(f"Failed to close position: {e}")
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        if not self.api:
            raise RuntimeError("Not connected to broker")
        
        clock = self.api.get_clock()
        return clock.is_open

