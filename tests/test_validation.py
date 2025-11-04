"""
Tests for validation module.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from validation import OHLCVValidator, validate_ohlcv, ValidationError


class TestOHLCVValidator:
    """Test OHLCV data validation"""
    
    def test_valid_data(self, sample_ohlcv_data):
        """Test validation passes for valid data"""
        errors = OHLCVValidator.validate(sample_ohlcv_data, strict=False)
        assert len(errors) == 0
        assert OHLCVValidator.is_valid(sample_ohlcv_data)
    
    def test_empty_dataframe(self):
        """Test validation fails for empty DataFrame"""
        df = pd.DataFrame()
        errors = OHLCVValidator.validate(df, strict=False)
        
        assert len(errors) > 0
        assert any(e.error_type == 'empty' for e in errors)
        assert not OHLCVValidator.is_valid(df)
    
    def test_empty_dataframe_strict(self):
        """Test strict mode raises on empty DataFrame"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame is empty"):
            OHLCVValidator.validate(df, strict=True)
    
    def test_missing_columns(self):
        """Test validation fails for missing columns"""
        df = pd.DataFrame({
            'open': [100, 101],
            'close': [101, 102]
            # Missing high, low, volume
        })
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert len(errors) > 0
        assert any(e.error_type == 'missing' for e in errors)
        assert not OHLCVValidator.is_valid(df)
    
    def test_missing_columns_strict(self):
        """Test strict mode raises on missing columns"""
        df = pd.DataFrame({'open': [100]})
        
        with pytest.raises(ValueError, match="Missing required columns"):
            OHLCVValidator.validate(df, strict=True)
    
    def test_null_values(self):
        """Test validation detects null values"""
        dates = pd.date_range(end=datetime.now(), periods=5, freq='5min')
        df = pd.DataFrame({
            'open': [100, 101, None, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'close': [100, 101, 102, 103, 104],
            'volume': [1000, 1100, 1200, 1300, 1400]
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'null_values' and e.field == 'open' for e in errors)
    
    def test_negative_prices(self):
        """Test validation detects negative prices"""
        dates = pd.date_range(end=datetime.now(), periods=3, freq='5min')
        df = pd.DataFrame({
            'open': [100, -101, 102],  # Negative price
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'invalid_value' and e.field == 'open' for e in errors)
    
    def test_negative_volume(self):
        """Test validation detects negative volume"""
        dates = pd.date_range(end=datetime.now(), periods=3, freq='5min')
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, -1100, 1200]  # Negative volume
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'invalid_value' and e.field == 'volume' for e in errors)
    
    def test_high_low_relationship(self):
        """Test validation checks high >= low"""
        dates = pd.date_range(end=datetime.now(), periods=3, freq='5min')
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 100, 103],  # High < low at index 1
            'low': [99, 102, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'logical_error' and 'high < low' in e.message for e in errors)
    
    def test_close_in_range(self):
        """Test validation checks close is within high/low range"""
        dates = pd.date_range(end=datetime.now(), periods=3, freq='5min')
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [105, 101, 102],  # Close > high at index 0
            'volume': [1000, 1100, 1200]
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'logical_error' and e.field == 'close' for e in errors)
    
    def test_open_in_range(self):
        """Test validation checks open is within high/low range"""
        dates = pd.date_range(end=datetime.now(), periods=3, freq='5min')
        df = pd.DataFrame({
            'open': [95, 101, 102],  # Open < low at index 0
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'logical_error' and e.field == 'open' for e in errors)
    
    def test_datetime_index(self):
        """Test validation checks for datetime index"""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        })
        # No datetime index set
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'wrong_type' and e.field == 'index' for e in errors)
    
    def test_duplicate_timestamps(self):
        """Test validation detects duplicate timestamps"""
        # Create a specific time and repeat it
        base_time = datetime(2025, 1, 1, 10, 0, 0)
        dates = pd.DatetimeIndex([
            base_time,
            base_time,  # Duplicate
            base_time + timedelta(minutes=5)
        ])
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        }, index=dates)
        
        # Verify we have duplicates
        assert df.index.duplicated().any(), "Test setup should have duplicate timestamps"
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'duplicates' for e in errors)
    
    def test_convenience_function(self, sample_ohlcv_data):
        """Test convenience function"""
        errors = validate_ohlcv(sample_ohlcv_data, strict=False)
        assert len(errors) == 0
    
    def test_wrong_data_types(self):
        """Test validation detects wrong data types"""
        dates = pd.date_range(end=datetime.now(), periods=3, freq='5min')
        df = pd.DataFrame({
            'open': ['100', '101', '102'],  # Strings instead of numbers
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        }, index=dates)
        
        errors = OHLCVValidator.validate(df, strict=False)
        assert any(e.error_type == 'wrong_type' and e.field == 'open' for e in errors)

