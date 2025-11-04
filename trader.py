"""
Main trading bot that combines strategy, data, and broker integration.
This is the main entry point for live trading.
"""
from datetime import datetime
from typing import Dict, Optional
from strategy import TradingStrategy
from data_fetcher import DataFetcher
from broker import Broker
from config import Config


class Trader:
    """
    Main trading bot that monitors signals and executes trades.
    Combines strategy analysis with broker integration.
    """
    
    def __init__(self, symbol: str, config: Optional[Config] = None, 
                 paper_trading: bool = True):
        """
        Initialize trader.
        
        Args:
            symbol: Stock ticker to trade
            config: Configuration object
            paper_trading: Use paper trading account
        """
        self.symbol = symbol.upper()
        self.config = config or Config()
        self.strategy = TradingStrategy(self.config)
        self.data_fetcher = DataFetcher(source='alpaca')
        self.broker = Broker(self.config, paper_trading=paper_trading)
        self.positions = {}
    
    def analyze_current_market(self) -> Dict:
        """
        Analyze current market conditions and generate signal.
        
        Returns:
            Dictionary with current signal and market analysis
        """
        # Fetch recent data
        df = self.data_fetcher.fetch_data(self.symbol, period=5)
        
        # Get current signal
        signal_info = self.strategy.get_current_signal(df)
        
        # Get current price from broker
        try:
            current_price = self.broker.get_current_price(self.symbol)
            signal_info['broker_price'] = current_price
        except:
            signal_info['broker_price'] = signal_info['price']
        
        return signal_info
    
    def check_and_execute(self, dry_run: bool = True) -> Dict:
        """
        Check market conditions and execute trades if signals are generated.
        
        Args:
            dry_run: If True, only simulate trades without executing
            
        Returns:
            Dictionary with action taken and results
        """
        if not self.broker.is_market_open():
            return {
                'action': 'market_closed',
                'message': 'Market is currently closed'
            }
        
        # Analyze market
        signal_info = self.analyze_current_market()
        
        # Check existing positions
        positions = self.broker.get_positions()
        symbol_position = next((p for p in positions if p['symbol'] == self.symbol), None)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'signal': signal_info['signal'],
            'signal_value': signal_info['signal_value'],
            'price': signal_info.get('broker_price', signal_info['price']),
            'rsi': signal_info['rsi'],
            'dry_run': dry_run
        }
        
        # Handle buy signal
        if signal_info['signal'] == 'buy' and symbol_position is None:
            # Calculate position size
            account_info = self.broker.get_account_info()
            risk_amount = account_info['buying_power'] * self.config.RISK_PER_TRADE
            entry_price = signal_info['price']
            stop_loss_price = signal_info.get('stop_loss', entry_price * (1 - self.config.STOP_LOSS_PCT))
            risk_per_share = entry_price - stop_loss_price
            
            if risk_per_share > 0:
                shares = int(risk_amount / risk_per_share)
                max_shares = int(self.config.MAX_POSITION_SIZE / entry_price)
                shares = min(shares, max_shares)
                
                if shares > 0:
                    if dry_run:
                        result['action'] = 'buy_signal'
                        result['message'] = f'Would buy {shares} shares at ${entry_price:.2f}'
                        result['shares'] = shares
                        result['estimated_cost'] = shares * entry_price
                    else:
                        order = self.broker.place_order(
                            symbol=self.symbol,
                            qty=shares,
                            side='buy',
                            order_type='market'
                        )
                        result['action'] = 'buy_executed'
                        result['order'] = order
                        result['message'] = f'Bought {shares} shares'
        
        # Handle sell signal
        elif signal_info['signal'] == 'sell' and symbol_position is not None:
            if dry_run:
                result['action'] = 'sell_signal'
                result['message'] = f'Would sell {symbol_position["qty"]} shares at ${signal_info["price"]:.2f}'
            else:
                order = self.broker.close_position(self.symbol)
                result['action'] = 'sell_executed'
                result['order'] = order
                result['message'] = f'Sold position'
        
        # Check stop loss and take profit for existing position
        elif symbol_position is not None:
            entry_price = symbol_position['avg_entry_price']
            current_price = signal_info.get('broker_price', signal_info['price'])
            
            stop_loss_price = entry_price * (1 - self.config.STOP_LOSS_PCT)
            take_profit_price = entry_price * (1 + self.config.TAKE_PROFIT_PCT)
            
            if current_price <= stop_loss_price:
                if dry_run:
                    result['action'] = 'stop_loss_triggered'
                    result['message'] = f'Stop loss would trigger at ${current_price:.2f}'
                else:
                    order = self.broker.close_position(self.symbol)
                    result['action'] = 'stop_loss_executed'
                    result['order'] = order
                    result['message'] = 'Stop loss executed'
            
            elif current_price >= take_profit_price:
                if dry_run:
                    result['action'] = 'take_profit_triggered'
                    result['message'] = f'Take profit would trigger at ${current_price:.2f}'
                else:
                    order = self.broker.close_position(self.symbol)
                    result['action'] = 'take_profit_executed'
                    result['order'] = order
                    result['message'] = 'Take profit executed'
            
            else:
                result['action'] = 'hold'
                result['message'] = f'Holding position. Current P&L: ${symbol_position["unrealized_pl"]:.2f}'
                result['unrealized_pl'] = symbol_position['unrealized_pl']
        
        else:
            result['action'] = 'hold'
            result['message'] = 'No signal, holding cash'
        
        return result
    
    def get_status(self) -> Dict:
        """Get current trading status"""
        account_info = self.broker.get_account_info()
        positions = self.broker.get_positions()
        signal_info = self.analyze_current_market()
        
        return {
            'account': account_info,
            'positions': positions,
            'current_signal': signal_info,
            'symbol': self.symbol,
            'market_open': self.broker.is_market_open()
        }

