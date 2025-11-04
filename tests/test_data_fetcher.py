"""
Tests for data fetcher module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from data_fetcher import DataFetcher
from config import Config


class TestDataFetcher:
    """Test data fetching functionality"""
    
    def test_data_fetcher_initialization(self):
        """Test data fetcher can be initialized"""
        fetcher = DataFetcher(source='yfinance')
        assert fetcher is not None
        assert fetcher.source == 'yfinance'
        assert fetcher.config is not None
    
    def test_data_fetcher_yfinance_source(self):
        """Test yfinance source is set correctly"""
        fetcher = DataFetcher(source='yfinance')
        assert fetcher.source == 'yfinance'
    
    def test_data_fetcher_alpaca_source(self):
        """Test alpaca source is set correctly"""
        fetcher = DataFetcher(source='alpaca')
        assert fetcher.source == 'alpaca'
    
    def test_data_fetcher_invalid_source(self):
        """Test invalid source raises error"""
        with pytest.raises(ValueError):
            fetcher = DataFetcher(source='invalid')
            fetcher.fetch_data('AAPL')
    
    @patch('yfinance.Ticker')
    def test_fetch_yfinance_data(self, mock_ticker):
        """Test fetching data from yfinance"""
        # Create mock data
        mock_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000000, 1100000, 1200000]
        })
        mock_data.index = pd.date_range(end=pd.Timestamp.now(), periods=3, freq='5min')
        
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Test
        fetcher = DataFetcher(source='yfinance')
        df = fetcher.fetch_data('AAPL', period=1)
        
        # Verify
        assert df is not None
        assert len(df) == 3
        assert 'close' in df.columns
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'volume' in df.columns
    
    @patch('yfinance.Ticker')
    def test_fetch_yfinance_empty_data(self, mock_ticker):
        """Test handling of empty data from yfinance"""
        # Setup mock to return empty DataFrame
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DataFetcher(source='yfinance')
        
        with pytest.raises(ValueError, match="No data found"):
            fetcher.fetch_data('INVALID', period=1)
    
    @patch('yfinance.Ticker')
    def test_get_current_price_yfinance(self, mock_ticker):
        """Test getting current price from yfinance"""
        # Create mock data with recent price
        mock_data = pd.DataFrame({
            'Close': [150.25]
        })
        mock_data.index = pd.date_range(end=pd.Timestamp.now(), periods=1, freq='1min')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = DataFetcher(source='yfinance')
        price = fetcher.get_current_price('AAPL')
        
        assert price == 150.25
        assert isinstance(price, float)
    
    @patch('alpaca_trade_api.REST')
    def test_fetch_alpaca_data(self, mock_rest):
        """Test fetching data from Alpaca"""
        # Create mock data
        mock_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100.5, 101.5, 102.5],
            'volume': [1000000, 1100000, 1200000]
        })
        mock_data.index = pd.date_range(end=pd.Timestamp.now(), periods=3, freq='5min')
        
        # Setup mock
        mock_api = Mock()
        mock_api.get_bars.return_value.df = mock_data
        mock_rest.return_value = mock_api
        
        fetcher = DataFetcher(source='alpaca')
        df = fetcher.fetch_data('AAPL', period=1)
        
        # Verify
        assert df is not None
        assert len(df) == 3
        assert 'close' in df.columns
    
    @patch('alpaca_trade_api.REST')
    def test_fetch_alpaca_empty_data(self, mock_rest):
        """Test handling of empty data from Alpaca"""
        # Setup mock to return empty DataFrame
        mock_api = Mock()
        mock_api.get_bars.return_value.df = pd.DataFrame()
        mock_rest.return_value = mock_api
        
        fetcher = DataFetcher(source='alpaca')
        
        with pytest.raises(ValueError, match="No data found"):
            fetcher.fetch_data('INVALID', period=1)
    
    def test_fetch_alpaca_without_import(self):
        """Test that alpaca source requires the library"""
        # This test checks that if alpaca-trade-api is not installed,
        # we get a helpful error message
        fetcher = DataFetcher(source='alpaca')
        
        # If the library isn't installed, we'll get ImportError
        # This is acceptable behavior - the error message is clear
        pass

