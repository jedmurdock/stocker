"""
Tests for trading strategy module.
"""
import pytest
import pandas as pd
import numpy as np
from strategy import TradingStrategy
from config import Config


class TestTradingStrategy:
    """Test trading strategy calculations and signals"""
    
    def test_strategy_initialization(self):
        """Test strategy can be initialized"""
        strategy = TradingStrategy()
        assert strategy is not None
        assert strategy.config is not None
    
    def test_calculate_indicators(self, sample_ohlcv_data):
        """Test that indicators are calculated correctly"""
        strategy = TradingStrategy()
        df_with_indicators = strategy.calculate_indicators(sample_ohlcv_data)
        
        # Check that indicators are added
        assert 'rsi' in df_with_indicators.columns
        assert 'fast_ma' in df_with_indicators.columns
        assert 'slow_ma' in df_with_indicators.columns
        
        # Check that RSI values are in valid range
        rsi_values = df_with_indicators['rsi'].dropna()
        assert (rsi_values >= 0).all()
        assert (rsi_values <= 100).all()
        
        # Check that moving averages are calculated
        assert not df_with_indicators['fast_ma'].isna().all()
        assert not df_with_indicators['slow_ma'].isna().all()
    
    def test_rsi_calculation(self, sample_ohlcv_data):
        """Test RSI calculation is reasonable"""
        strategy = TradingStrategy()
        df_with_indicators = strategy.calculate_indicators(sample_ohlcv_data)
        
        # RSI should be between 0 and 100
        rsi = df_with_indicators['rsi'].dropna()
        assert len(rsi) > 0
        assert rsi.min() >= 0
        assert rsi.max() <= 100
    
    def test_moving_averages_order(self, sample_ohlcv_data_with_trend):
        """Test that fast MA responds faster than slow MA"""
        strategy = TradingStrategy()
        df_with_indicators = strategy.calculate_indicators(sample_ohlcv_data_with_trend)
        
        # In an uptrend, fast MA should generally be above slow MA
        # (at least near the end)
        recent_data = df_with_indicators.tail(20)
        fast_above_slow = (recent_data['fast_ma'] > recent_data['slow_ma']).sum()
        
        # Should have at least some periods where fast > slow in uptrend
        assert fast_above_slow > 0
    
    def test_generate_signals(self, sample_ohlcv_data):
        """Test that signals are generated"""
        strategy = TradingStrategy()
        analyzed_df = strategy.analyze(sample_ohlcv_data)
        
        # Check signal column exists
        assert 'signal' in analyzed_df.columns
        
        # Check signal values are valid (-1, 0, or 1)
        signals = analyzed_df['signal'].dropna()
        assert signals.isin([-1, 0, 1]).all()
    
    def test_buy_signal_conditions(self, sample_ohlcv_data):
        """Test buy signal logic"""
        strategy = TradingStrategy()
        analyzed_df = strategy.analyze(sample_ohlcv_data)
        
        buy_signals = analyzed_df[analyzed_df['signal'] == 1]
        
        if len(buy_signals) > 0:
            # When buy signal occurs, RSI should be above oversold
            assert (buy_signals['rsi'] > strategy.config.RSI_OVERSOLD).all()
            
            # Fast MA should be above slow MA
            assert (buy_signals['fast_ma'] > buy_signals['slow_ma']).all()
    
    def test_sell_signal_conditions(self, sample_ohlcv_data):
        """Test sell signal logic"""
        strategy = TradingStrategy()
        analyzed_df = strategy.analyze(sample_ohlcv_data)
        
        sell_signals = analyzed_df[analyzed_df['signal'] == -1]
        
        if len(sell_signals) > 0:
            # Sell signals should occur when RSI is overbought OR MA crossover
            # At least one condition should be true
            overbought = sell_signals['rsi'] > strategy.config.RSI_OVERBOUGHT
            bearish_crossover = sell_signals['fast_ma'] < sell_signals['slow_ma']
            
            # At least one condition should be true for sell signals
            assert (overbought | bearish_crossover).any() or len(sell_signals) == 0
    
    def test_get_current_signal(self, sample_ohlcv_data):
        """Test getting current signal information"""
        strategy = TradingStrategy()
        signal_info = strategy.get_current_signal(sample_ohlcv_data)
        
        # Check required fields
        assert 'signal' in signal_info
        assert 'price' in signal_info
        assert 'rsi' in signal_info
        assert 'timestamp' in signal_info
        
        # Check signal value
        assert signal_info['signal'] in ['buy', 'sell', 'hold']
        
        # Check price is positive
        assert signal_info['price'] > 0
        
        # Check RSI is in valid range
        assert 0 <= signal_info['rsi'] <= 100
    
    def test_get_current_signal_buy_stop_loss(self, sample_ohlcv_data):
        """Test that buy signals include stop loss and take profit"""
        strategy = TradingStrategy()
        
        # Create data that will generate a buy signal
        # (This is tricky without mocking, so we'll test the structure)
        signal_info = strategy.get_current_signal(sample_ohlcv_data)
        
        if signal_info['signal'] == 'buy':
            assert 'stop_loss' in signal_info
            assert 'take_profit' in signal_info
            assert signal_info['stop_loss'] < signal_info['price']
            assert signal_info['take_profit'] > signal_info['price']
    
    def test_analyze_completeness(self, sample_ohlcv_data):
        """Test that analyze method returns complete data"""
        strategy = TradingStrategy()
        analyzed_df = strategy.analyze(sample_ohlcv_data)
        
        # Should have all original columns plus indicators and signals
        original_cols = set(sample_ohlcv_data.columns)
        new_cols = {'rsi', 'fast_ma', 'slow_ma', 'signal'}
        
        assert original_cols.issubset(set(analyzed_df.columns))
        assert new_cols.issubset(set(analyzed_df.columns))
    
    def test_strategy_with_empty_data(self):
        """Test strategy handles empty data gracefully"""
        strategy = TradingStrategy()
        empty_df = pd.DataFrame()
        
        with pytest.raises((KeyError, IndexError, ValueError)):
            # Should raise an error with empty data
            strategy.analyze(empty_df)
    
    def test_strategy_with_minimal_data(self):
        """Test strategy with minimal data (should handle gracefully)"""
        strategy = TradingStrategy()
        
        # Create minimal dataset (less than RSI period)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=5, freq='5min')
        minimal_df = pd.DataFrame({
            'open': [100] * 5,
            'high': [101] * 5,
            'low': [99] * 5,
            'close': [100] * 5,
            'volume': [1000] * 5
        }, index=dates)
        
        # Should handle this, though indicators may have NaN values
        analyzed_df = strategy.analyze(minimal_df)
        assert analyzed_df is not None
        # Early rows will have NaN for indicators (need enough data for calculation)
        assert len(analyzed_df) == 5

