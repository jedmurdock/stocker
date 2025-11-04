"""
Configuration management for the trading system.
Loads settings from environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Trading system configuration"""
    
    # Alpaca API credentials
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Trading parameters
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', '0.02'))  # 2% of capital
    STOP_LOSS_PCT = float(os.getenv('STOP_LOSS_PCT', '0.02'))  # 2% stop loss
    TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT_PCT', '0.04'))  # 4% take profit
    
    # Strategy parameters (RSI + Moving Average)
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    FAST_MA_PERIOD = 9  # Fast moving average
    SLOW_MA_PERIOD = 21  # Slow moving average
    
    # Data parameters
    DATA_TIMEFRAME = '5m'  # 5-minute candles for day trading
    LOOKBACK_DAYS = 30  # Days of historical data to fetch

