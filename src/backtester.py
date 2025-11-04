"""
Backtesting framework for testing trading strategies on historical data.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from strategies import get_strategy, StrategyProfile, DEFAULT_STRATEGY
from data_fetcher import DataFetcher
from config import Config


class Backtester:
    """
    Backtesting engine for evaluating trading strategies.
    Simulates trades based on historical data and strategy signals.
    """
    
    def __init__(self, initial_capital: float = 10000, config: Optional[Config] = None,
                 strategy: Optional[StrategyProfile] = None, strategy_name: str = DEFAULT_STRATEGY):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital for backtest
            config: Configuration object
            strategy: Strategy instance (overrides strategy_name if provided)
            strategy_name: Name of strategy to use if strategy not provided
        """
        self.initial_capital = initial_capital
        self.config = config or Config()
        self.strategy = strategy or get_strategy(strategy_name, self.config)
        self.data_fetcher = DataFetcher(source='yfinance')
    
    def run_backtest(self, symbol: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> Dict:
        """
        Run a backtest on historical data.
        
        Args:
            symbol: Stock ticker to backtest
            start_date: Start date (YYYY-MM-DD), optional
            end_date: End date (YYYY-MM-DD), optional
            
        Returns:
            Dictionary with backtest results
        """
        # Fetch data (use longer period for meaningful backtests)
        # Default to 180 days if no dates specified
        fetch_period = 180 if not start_date else None
        df = self.data_fetcher.fetch_data(symbol, period=fetch_period) if fetch_period else self.data_fetcher.fetch_data(symbol)
        
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        if df.empty:
            raise ValueError(f"No data available for {symbol} in the specified date range")
        
        # Analyze data
        analyzed_df = self.strategy.analyze(df)
        
        # Simulate trading
        trades, portfolio_value = self._simulate_trades(analyzed_df)
        
        # Calculate performance metrics
        results = self._calculate_metrics(trades, portfolio_value, analyzed_df)
        
        return results
    
    def _simulate_trades(self, df: pd.DataFrame) -> tuple[List[Dict], pd.Series]:
        """
        Simulate trades based on signals.
        
        Returns:
            List of trades and portfolio value over time
        """
        capital = self.initial_capital
        position = None  # None, or {'shares': int, 'entry_price': float, 'entry_time': datetime}
        trades = []
        portfolio_values = []
        
        for idx, row in df.iterrows():
            current_price = row['close']
            signal = row['signal']
            
            # Check stop loss and take profit for existing position
            if position is not None:
                stop_loss = position['entry_price'] * (1 - self.config.STOP_LOSS_PCT)
                take_profit = position['entry_price'] * (1 + self.config.TAKE_PROFIT_PCT)
                
                if current_price <= stop_loss or current_price >= take_profit:
                    # Exit position
                    pnl = (current_price - position['entry_price']) * position['shares']
                    capital += current_price * position['shares']
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': idx,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'shares': position['shares'],
                        'pnl': pnl,
                        'return_pct': (current_price - position['entry_price']) / position['entry_price'] * 100,
                        'exit_reason': 'stop_loss' if current_price <= stop_loss else 'take_profit'
                    })
                    
                    position = None
            
            # Open new position on buy signal
            if signal == 1 and position is None:
                # Calculate position size based on risk
                risk_amount = capital * self.config.RISK_PER_TRADE
                stop_loss_price = current_price * (1 - self.config.STOP_LOSS_PCT)
                risk_per_share = current_price - stop_loss_price
                
                if risk_per_share > 0:
                    shares = int(risk_amount / risk_per_share)
                    max_shares = int(self.config.MAX_POSITION_SIZE / current_price)
                    shares = min(shares, max_shares)
                    
                    if shares > 0 and capital >= shares * current_price:
                        cost = shares * current_price
                        capital -= cost
                        position = {
                            'shares': shares,
                            'entry_price': current_price,
                            'entry_time': idx
                        }
            
            # Close position on sell signal
            elif signal == -1 and position is not None:
                pnl = (current_price - position['entry_price']) * position['shares']
                capital += current_price * position['shares']
                
                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': idx,
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'shares': position['shares'],
                    'pnl': pnl,
                    'return_pct': (current_price - position['entry_price']) / position['entry_price'] * 100,
                    'exit_reason': 'signal'
                })
                
                position = None
            
            # Calculate portfolio value
            portfolio_value = capital
            if position is not None:
                portfolio_value += position['shares'] * current_price
            
            portfolio_values.append(portfolio_value)
        
        # Close any remaining open position at the end of backtest
        if position is not None:
            final_price = df.iloc[-1]['close']
            pnl = (final_price - position['entry_price']) * position['shares']
            capital += final_price * position['shares']
            
            trades.append({
                'entry_time': position['entry_time'],
                'exit_time': df.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'shares': position['shares'],
                'pnl': pnl,
                'return_pct': (final_price - position['entry_price']) / position['entry_price'] * 100,
                'exit_reason': 'end_of_backtest'
            })
            
            # Update final portfolio value
            portfolio_values[-1] = capital
        
        portfolio_series = pd.Series(portfolio_values, index=df.index)
        
        return trades, portfolio_series
    
    def _calculate_metrics(self, trades: List[Dict], portfolio_value: pd.Series, 
                          df: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        if not trades:
            return {
                'initial_capital': self.initial_capital,
                'final_capital': self.initial_capital,
                'total_return': 0,
                'total_return_pct': 0,
                'num_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'max_drawdown': 0,
                'trades': [],
                'portfolio_value': {str(k): v for k, v in portfolio_value.to_dict().items()}
            }
        
        trades_df = pd.DataFrame(trades)
        
        # Basic metrics
        final_capital = portfolio_value.iloc[-1]
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Win rate
        winning_trades = trades_df[trades_df['pnl'] > 0]
        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0
        
        # Average return
        avg_return = trades_df['return_pct'].mean()
        
        # Maximum drawdown
        running_max = portfolio_value.expanding().max()
        drawdown = (portfolio_value - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': float(final_capital),
            'total_return': float(total_return),
            'total_return_pct': float(total_return_pct),
            'num_trades': len(trades),
            'win_rate': float(win_rate),
            'avg_return': float(avg_return),
            'max_drawdown': float(max_drawdown),
            'trades': trades,
            'portfolio_value': {str(k): v for k, v in portfolio_value.to_dict().items()}
        }

