"""
Data fetching module for stock market data.
Supports both yfinance (for backtesting) and Alpaca (for live trading).
"""
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
from config import Config


class DataFetcher:
    """Fetches stock market data from various sources"""
    
    def __init__(self, source: str = 'yfinance'):
        """
        Initialize data fetcher.
        
        Args:
            source: 'yfinance' for historical data, 'alpaca' for live data
        """
        self.source = source
        self.config = Config()
    
    def fetch_data(self, symbol: str, period: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch historical stock data.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            period: Number of days to look back (defaults to config)
            
        Returns:
            DataFrame with OHLCV data and datetime index
            
        Raises:
            ValueError: If symbol is invalid or data source is unknown
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if period is None:
            period = self.config.LOOKBACK_DAYS
        
        if period <= 0:
            raise ValueError(f"Period must be positive, got: {period}")
        
        if self.source == 'yfinance':
            return self._fetch_yfinance(symbol, period)
        elif self.source == 'alpaca':
            return self._fetch_alpaca(symbol, period)
        else:
            raise ValueError(f"Unknown data source: {self.source}")
    
    def _fetch_yfinance(self, symbol: str, period: int) -> pd.DataFrame:
        """Fetch data using yfinance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Use daily intervals for longer periods (yfinance limitation)
        # 5m data only available for ~7 days, 1h for ~730 days, 1d for years
        if period > 7:
            interval = '1d'
        else:
            interval = '1h'  # Use 1h instead of 5m for better reliability
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        
        # Clean and standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        df.index.name = 'datetime'
        
        return df
    
    def _fetch_alpaca(self, symbol: str, period: int) -> pd.DataFrame:
        """Fetch data using Alpaca API (for live trading)"""
        try:
            import alpaca_trade_api as tradeapi
            
            api = tradeapi.REST(
                self.config.ALPACA_API_KEY,
                self.config.ALPACA_SECRET_KEY,
                self.config.ALPACA_BASE_URL
            )
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            bars = api.get_bars(
                symbol,
                self.config.DATA_TIMEFRAME,
                start=start_date.isoformat(),
                end=end_date.isoformat()
            ).df
            
            if bars.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            
            # Standardize column names
            bars.columns = [col.lower() for col in bars.columns]
            bars.index.name = 'datetime'
            
            return bars
            
        except ImportError:
            raise ImportError("alpaca-trade-api not installed. Install with: pip install alpaca-trade-api")
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price of a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Current price as float
            
        Raises:
            ValueError: If price cannot be fetched
        """
        if self.source == 'yfinance':
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            if not data.empty:
                return float(data['Close'].iloc[-1])
            raise ValueError(f"Could not fetch current price for {symbol}")
        elif self.source == 'alpaca':
            try:
                import alpaca_trade_api as tradeapi
                api = tradeapi.REST(
                    self.config.ALPACA_API_KEY,
                    self.config.ALPACA_SECRET_KEY,
                    self.config.ALPACA_BASE_URL
                )
                quote = api.get_latest_quote(symbol)
                return float(quote.bp)  # Use bid price
            except Exception as e:
                raise ValueError(f"Could not fetch current price for {symbol}: {e}")
        else:
            raise ValueError(f"Unknown data source: {self.source}")

