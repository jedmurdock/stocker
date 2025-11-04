"""
Trading strategy implementation using RSI + Moving Average crossover.
This is a conservative day trading strategy that combines:
- RSI for oversold/overbought conditions
- Moving average crossover for trend confirmation
"""
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from typing import Dict, Optional, Any
from config import Config


class TradingStrategy:
    """
    Conservative RSI + Moving Average trading strategy.
    
    Buy signals:
    - RSI crosses above oversold level (30) AND
    - Fast MA crosses above Slow MA (bullish crossover) AND
    - Price is above both MAs
    
    Sell signals:
    - RSI crosses above overbought level (70) OR
    - Fast MA crosses below Slow MA (bearish crossover) OR
    - Stop loss or take profit hit
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize strategy with configuration"""
        self.config = config or Config()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the strategy.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
            
        Raises:
            ValueError: If df is empty or missing required columns
        """
        if df.empty:
            raise ValueError("Cannot calculate indicators on empty DataFrame")
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"DataFrame missing required columns: {missing_columns}")
        
        df = df.copy()
        
        # Calculate RSI
        rsi_indicator = RSIIndicator(close=df['close'], window=self.config.RSI_PERIOD)
        df['rsi'] = rsi_indicator.rsi()
        
        # Calculate Moving Averages
        fast_ma = SMAIndicator(close=df['close'], window=self.config.FAST_MA_PERIOD)
        slow_ma = SMAIndicator(close=df['close'], window=self.config.SLOW_MA_PERIOD)
        df['fast_ma'] = fast_ma.sma_indicator()
        df['slow_ma'] = slow_ma.sma_indicator()
        
        # Calculate previous values for crossover detection
        df['rsi_prev'] = df['rsi'].shift(1)
        df['fast_ma_prev'] = df['fast_ma'].shift(1)
        df['slow_ma_prev'] = df['slow_ma'].shift(1)
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on strategy rules.
        
        Args:
            df: DataFrame with indicators calculated
            
        Returns:
            DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        df = df.copy()
        df['signal'] = 0
        
        # Buy conditions
        buy_condition = (
            (df['rsi'] > self.config.RSI_OVERSOLD) &  # RSI above oversold
            (df['rsi_prev'] <= self.config.RSI_OVERSOLD) &  # RSI just crossed above oversold
            (df['fast_ma'] > df['slow_ma']) &  # Fast MA above Slow MA
            (df['fast_ma_prev'] <= df['slow_ma_prev']) &  # MA crossover just occurred
            (df['close'] > df['fast_ma']) &  # Price above fast MA
            (df['close'] > df['slow_ma'])  # Price above slow MA
        )
        
        # Sell conditions
        sell_condition = (
            (df['rsi'] > self.config.RSI_OVERBOUGHT) |  # RSI overbought
            ((df['fast_ma'] < df['slow_ma']) &  # Fast MA below Slow MA
            (df['fast_ma_prev'] >= df['slow_ma_prev']))  # Bearish crossover
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        return df
    
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete analysis: calculate indicators and generate signals.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with indicators and signals
        """
        df_with_indicators = self.calculate_indicators(df)
        df_with_signals = self.generate_signals(df_with_indicators)
        return df_with_signals
    
    def get_current_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get the most recent trading signal.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with signal information
            
        Raises:
            ValueError: If df is empty
        """
        if df.empty:
            raise ValueError("Cannot generate signal from empty DataFrame")
        
        analyzed_df = self.analyze(df)
        latest = analyzed_df.iloc[-1]
        
        signal_value = latest['signal']
        
        result = {
            'signal': 'hold',
            'signal_value': signal_value,
            'price': latest['close'],
            'rsi': latest['rsi'],
            'fast_ma': latest['fast_ma'],
            'slow_ma': latest['slow_ma'],
            'timestamp': latest.name
        }
        
        if signal_value == 1:
            result['signal'] = 'buy'
            result['stop_loss'] = latest['close'] * (1 - self.config.STOP_LOSS_PCT)
            result['take_profit'] = latest['close'] * (1 + self.config.TAKE_PROFIT_PCT)
        elif signal_value == -1:
            result['signal'] = 'sell'
        
        return result

