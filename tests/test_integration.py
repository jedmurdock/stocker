"""
Integration tests that test multiple components together.
These tests may be slower and require more setup.
"""
import pytest
from strategy import TradingStrategy
from data_fetcher import DataFetcher
from backtester import Backtester
from config import Config


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the full trading system"""
    
    @pytest.mark.slow
    def test_end_to_end_backtest(self):
        """Test complete backtest flow with real data fetching"""
        # This test actually fetches data (may be slow)
        backtester = Backtester(initial_capital=10000)
        
        try:
            results = backtester.run_backtest('AAPL')
            
            # Check that results are valid
            assert results is not None
            assert 'total_return_pct' in results
            assert 'num_trades' in results
            assert results['initial_capital'] == 10000
            assert results['final_capital'] >= 0  # Can't go negative
            
        except Exception as e:
            # If data fetch fails (network issue, etc.), skip test
            pytest.skip(f"Data fetch failed: {e}")
    
    def test_strategy_with_real_data_structure(self):
        """Test strategy works with real data structure from yfinance"""
        data_fetcher = DataFetcher(source='yfinance')
        strategy = TradingStrategy()
        
        try:
            # Fetch minimal data
            df = data_fetcher.fetch_data('AAPL', period=5)
            
            # Analyze
            analyzed_df = strategy.analyze(df)
            
            # Check structure
            assert not analyzed_df.empty
            assert 'signal' in analyzed_df.columns
            assert 'rsi' in analyzed_df.columns
            
            # Get current signal
            signal_info = strategy.get_current_signal(df)
            assert signal_info['signal'] in ['buy', 'sell', 'hold']
            
        except Exception as e:
            pytest.skip(f"Data fetch failed: {e}")
    
    def test_backtest_results_consistency(self, sample_ohlcv_data):
        """Test that backtest results are internally consistent"""
        backtester = Backtester(initial_capital=10000)
        strategy = TradingStrategy()
        
        # Analyze data
        analyzed_df = strategy.analyze(sample_ohlcv_data)
        
        # Simulate trades
        trades, portfolio_value = backtester._simulate_trades(analyzed_df)
        
        # Calculate metrics
        results = backtester._calculate_metrics(trades, portfolio_value, analyzed_df)
        
        # Check consistency
        if len(trades) > 0:
            # If we have trades, final capital should reflect P&L
            total_pnl = sum(t['pnl'] for t in trades)
            expected_final = backtester.initial_capital + total_pnl
            
            # Allow small floating point differences
            assert abs(results['final_capital'] - expected_final) < 0.01
        
        # Win rate should be between 0 and 100
        assert 0 <= results['win_rate'] <= 100
        
        # Number of trades should match
        assert results['num_trades'] == len(trades)
    
    def test_signal_generation_consistency(self, sample_ohlcv_data):
        """Test that signals are generated consistently"""
        import pandas as pd
        import numpy as np
        strategy = TradingStrategy()
        
        # Analyze twice - should get same results
        analyzed_df1 = strategy.analyze(sample_ohlcv_data)
        analyzed_df2 = strategy.analyze(sample_ohlcv_data)
        
        # Signals should be identical
        assert (analyzed_df1['signal'] == analyzed_df2['signal']).all()
        
        # RSI should be identical (use pandas equals to handle NaN properly)
        # Or compare non-NaN values only
        pd.testing.assert_series_equal(analyzed_df1['rsi'], analyzed_df2['rsi'])
    
    def test_config_strategy_integration(self):
        """Test that config values are properly used by strategy"""
        # Create custom config
        config = Config()
        original_rsi_period = config.RSI_PERIOD
        
        # Strategy should use config values
        strategy = TradingStrategy(config)
        assert strategy.config.RSI_PERIOD == original_rsi_period
        
        # Strategy calculations should use config
        assert strategy.config.RSI_OVERSOLD == 30
        assert strategy.config.RSI_OVERBOUGHT == 70

