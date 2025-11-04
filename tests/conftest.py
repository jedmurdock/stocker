"""
Pytest configuration and shared fixtures.
"""
import sys
from pathlib import Path

# Add src directory to path for tests
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='5min')
    
    # Create realistic price data with some trend
    base_price = 100.0
    prices = []
    for i in range(100):
        # Add some trend and noise
        trend = i * 0.01
        noise = np.random.normal(0, 0.5)
        price = base_price + trend + noise
        prices.append(max(price, 1.0))  # Ensure positive prices
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    
    return df


@pytest.fixture
def sample_ohlcv_data_with_trend():
    """Create sample OHLCV data with clear uptrend for testing signals"""
    dates = pd.date_range(end=datetime.now(), periods=50, freq='5min')
    
    # Create uptrending data
    prices = []
    for i in range(50):
        price = 100.0 + (i * 0.1) + np.random.normal(0, 0.3)
        prices.append(max(price, 1.0))
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 50)
    }, index=dates)
    
    return df


@pytest.fixture
def sample_ohlcv_data_with_downtrend():
    """Create sample OHLCV data with clear downtrend"""
    dates = pd.date_range(end=datetime.now(), periods=50, freq='5min')
    
    # Create downtrending data
    prices = []
    for i in range(50):
        price = 100.0 - (i * 0.1) + np.random.normal(0, 0.3)
        prices.append(max(price, 1.0))
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 50)
    }, index=dates)
    
    return df


@pytest.fixture
def mock_config():
    """Create a mock configuration object"""
    from config import Config
    
    # Save original env vars if needed
    config = Config()
    return config

