"""
Tests for backtesting module.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from backtester import Backtester
from strategy import TradingStrategy


class TestBacktester:
    """Test backtesting functionality"""
    
    def test_backtester_initialization(self):
        """Test backtester can be initialized"""
        backtester = Backtester(initial_capital=10000)
        assert backtester is not None
        assert backtester.initial_capital == 10000
        assert backtester.config is not None
        assert backtester.strategy is not None
    
    def test_backtester_default_capital(self):
        """Test backtester with default capital"""
        backtester = Backtester()
        assert backtester.initial_capital == 10000
    
    def test_simulate_trades_no_signals(self, sample_ohlcv_data):
        """Test simulation with no trading signals"""
        backtester = Backtester(initial_capital=10000)
        
        # Create data with no signals
        strategy = TradingStrategy()
        analyzed_df = strategy.analyze(sample_ohlcv_data)
        # Remove all signals
        analyzed_df['signal'] = 0
        
        trades, portfolio_value = backtester._simulate_trades(analyzed_df)
        
        # Should have no trades
        assert len(trades) == 0
        
        # Portfolio value should remain constant (no trades)
        assert portfolio_value.iloc[-1] == backtester.initial_capital
    
    def test_simulate_trades_buy_signal(self):
        """Test simulation with buy signal"""
        backtester = Backtester(initial_capital=10000)
        
        # Create simple data with buy signal
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='5min')
        prices = [100 + i * 0.1 for i in range(30)]  # Uptrend
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [1000000] * 30
        }, index=dates)
        
        strategy = TradingStrategy()
        analyzed_df = strategy.analyze(df)
        
        # Force a buy signal at a specific point
        analyzed_df.loc[analyzed_df.index[20], 'signal'] = 1
        
        trades, portfolio_value = backtester._simulate_trades(analyzed_df)
        
        # May or may not have trades depending on conditions
        # But if there are trades, they should be valid
        if len(trades) > 0:
            assert all(t['entry_price'] > 0 for t in trades)
            assert all(t['shares'] > 0 for t in trades)
    
    def test_calculate_metrics_no_trades(self):
        """Test metrics calculation with no trades"""
        backtester = Backtester(initial_capital=10000)
        
        trades = []
        portfolio_value = pd.Series([10000] * 100)
        df = pd.DataFrame()
        
        results = backtester._calculate_metrics(trades, portfolio_value, df)
        
        assert results['initial_capital'] == 10000
        assert results['final_capital'] == 10000
        assert results['total_return'] == 0
        assert results['total_return_pct'] == 0
        assert results['num_trades'] == 0
        assert results['win_rate'] == 0
        assert len(results['trades']) == 0
    
    def test_calculate_metrics_with_trades(self):
        """Test metrics calculation with sample trades"""
        backtester = Backtester(initial_capital=10000)
        
        # Create sample trades
        trades = [
            {
                'entry_time': pd.Timestamp('2024-01-01'),
                'exit_time': pd.Timestamp('2024-01-02'),
                'entry_price': 100.0,
                'exit_price': 102.0,
                'shares': 10,
                'pnl': 20.0,
                'return_pct': 2.0,
                'exit_reason': 'take_profit'
            },
            {
                'entry_time': pd.Timestamp('2024-01-03'),
                'exit_time': pd.Timestamp('2024-01-04'),
                'entry_price': 100.0,
                'exit_price': 98.0,
                'shares': 10,
                'pnl': -20.0,
                'return_pct': -2.0,
                'exit_reason': 'stop_loss'
            }
        ]
        
        portfolio_value = pd.Series([10000, 10020, 10000, 9980, 9980])
        df = pd.DataFrame()
        
        results = backtester._calculate_metrics(trades, portfolio_value, df)
        
        assert results['num_trades'] == 2
        assert results['win_rate'] == 50.0  # 1 win, 1 loss
        assert results['avg_return'] == 0.0  # (2.0 + -2.0) / 2
        assert len(results['trades']) == 2
    
    @patch('backtester.DataFetcher')
    def test_run_backtest_structure(self, mock_data_fetcher):
        """Test that run_backtest returns correct structure"""
        # Create mock data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='5min')
        prices = [100 + i * 0.1 for i in range(50)]
        
        mock_df = pd.DataFrame({
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [1000000] * 50
        }, index=dates)
        
        # Setup mock
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_data.return_value = mock_df
        mock_data_fetcher.return_value = mock_fetcher
        
        backtester = Backtester(initial_capital=10000)
        results = backtester.run_backtest('AAPL')
        
        # Check structure
        assert 'initial_capital' in results
        assert 'final_capital' in results
        assert 'total_return' in results
        assert 'total_return_pct' in results
        assert 'num_trades' in results
        assert 'win_rate' in results
        assert 'avg_return' in results
        assert 'max_drawdown' in results
        assert 'trades' in results
        assert 'portfolio_value' in results
        
        # Check types
        assert isinstance(results['initial_capital'], (int, float))
        assert isinstance(results['final_capital'], (int, float))
        assert isinstance(results['num_trades'], int)
        assert isinstance(results['trades'], list)
    
    @patch('backtester.DataFetcher')
    def test_run_backtest_empty_data(self, mock_data_fetcher):
        """Test backtest with empty data"""
        # Setup mock to return empty DataFrame
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_data.return_value = pd.DataFrame()
        mock_data_fetcher.return_value = mock_fetcher
        
        backtester = Backtester(initial_capital=10000)
        
        with pytest.raises(ValueError):
            backtester.run_backtest('INVALID')
    
    @patch('backtester.DataFetcher')
    def test_run_backtest_with_date_range(self, mock_data_fetcher):
        """Test backtest with date filtering"""
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='5min')
        prices = [100 + i * 0.01 for i in range(len(dates))]
        
        mock_df = pd.DataFrame({
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [1000000] * len(dates)
        }, index=dates)
        
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_data.return_value = mock_df
        mock_data_fetcher.return_value = mock_fetcher
        
        backtester = Backtester(initial_capital=10000)
        results = backtester.run_backtest('AAPL', start_date='2024-01-15', end_date='2024-01-20')
        
        # Should complete without error
        assert results is not None
        assert 'num_trades' in results

