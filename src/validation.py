"""
DataFrame schema validation for the trading system.
Ensures data integrity and catches issues early.
"""
import pandas as pd
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error"""
    field: str
    error_type: str
    message: str


class OHLCVValidator:
    """
    Validator for OHLCV (Open, High, Low, Close, Volume) data.
    Ensures data meets expected format and constraints.
    """
    
    REQUIRED_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
    
    @classmethod
    def validate(cls, df: pd.DataFrame, strict: bool = True) -> List[ValidationError]:
        """
        Validate OHLCV DataFrame.
        
        Args:
            df: DataFrame to validate
            strict: If True, raise ValueError on first error. If False, collect all errors.
            
        Returns:
            List of validation errors (empty if valid)
            
        Raises:
            ValueError: If strict=True and validation fails
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            error = ValidationError('dataframe', 'empty', 'DataFrame is empty')
            errors.append(error)
            if strict:
                raise ValueError(f"Validation failed: {error.message}")
            return errors
        
        # Check required columns
        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            error = ValidationError(
                'columns',
                'missing',
                f"Missing required columns: {missing_cols}"
            )
            errors.append(error)
            if strict:
                raise ValueError(f"Validation failed: {error.message}")
            return errors  # Can't continue without columns
        
        # Check for null values
        for col in cls.REQUIRED_COLUMNS:
            null_count = df[col].isna().sum()
            if null_count > 0:
                error = ValidationError(
                    col,
                    'null_values',
                    f"Column '{col}' has {null_count} null values"
                )
                errors.append(error)
                if strict:
                    raise ValueError(f"Validation failed: {error.message}")
        
        # Check data types (should be numeric)
        for col in cls.REQUIRED_COLUMNS:
            if not pd.api.types.is_numeric_dtype(df[col]):
                error = ValidationError(
                    col,
                    'wrong_type',
                    f"Column '{col}' should be numeric, got {df[col].dtype}"
                )
                errors.append(error)
                if strict:
                    raise ValueError(f"Validation failed: {error.message}")
        
        # Only check numeric constraints if data types are correct
        if all(pd.api.types.is_numeric_dtype(df[col]) for col in cls.REQUIRED_COLUMNS):
            # Check for negative prices
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if (df[col] <= 0).any():
                    negative_count = (df[col] <= 0).sum()
                    error = ValidationError(
                        col,
                        'invalid_value',
                        f"Column '{col}' has {negative_count} non-positive values"
                    )
                    errors.append(error)
                    if strict:
                        raise ValueError(f"Validation failed: {error.message}")
            
            # Check for negative volume
            if (df['volume'] < 0).any():
                error = ValidationError(
                    'volume',
                    'invalid_value',
                    f"Volume has negative values"
                )
                errors.append(error)
                if strict:
                    raise ValueError(f"Validation failed: {error.message}")
        
            # Check OHLC relationships (High >= Low, etc.) - only if numeric
            invalid_hl = (df['high'] < df['low']).sum()
            if invalid_hl > 0:
                error = ValidationError(
                    'high_low',
                    'logical_error',
                    f"Found {invalid_hl} rows where high < low"
                )
                errors.append(error)
                if strict:
                    raise ValueError(f"Validation failed: {error.message}")
            
            invalid_close = ((df['close'] > df['high']) | (df['close'] < df['low'])).sum()
            if invalid_close > 0:
                error = ValidationError(
                    'close',
                    'logical_error',
                    f"Found {invalid_close} rows where close is outside high/low range"
                )
                errors.append(error)
                if strict:
                    raise ValueError(f"Validation failed: {error.message}")
            
            invalid_open = ((df['open'] > df['high']) | (df['open'] < df['low'])).sum()
            if invalid_open > 0:
                error = ValidationError(
                    'open',
                    'logical_error',
                    f"Found {invalid_open} rows where open is outside high/low range"
                )
                errors.append(error)
                if strict:
                    raise ValueError(f"Validation failed: {error.message}")
        
        # Check index (should be datetime)
        if not isinstance(df.index, pd.DatetimeIndex):
            error = ValidationError(
                'index',
                'wrong_type',
                f"Index should be DatetimeIndex, got {type(df.index)}"
            )
            errors.append(error)
            if strict:
                raise ValueError(f"Validation failed: {error.message}")
        
        # Check for duplicate timestamps
        if df.index.duplicated().any():
            dup_count = df.index.duplicated().sum()
            error = ValidationError(
                'index',
                'duplicates',
                f"Found {dup_count} duplicate timestamps"
            )
            errors.append(error)
            if strict:
                raise ValueError(f"Validation failed: {error.message}")
        
        return errors
    
    @classmethod
    def is_valid(cls, df: pd.DataFrame) -> bool:
        """
        Quick check if DataFrame is valid.
        
        Args:
            df: DataFrame to check
            
        Returns:
            True if valid, False otherwise
        """
        errors = cls.validate(df, strict=False)
        return len(errors) == 0


def validate_ohlcv(df: pd.DataFrame, strict: bool = True) -> List[ValidationError]:
    """
    Convenience function to validate OHLCV data.
    
    Args:
        df: DataFrame to validate
        strict: If True, raise on first error
        
    Returns:
        List of validation errors
    """
    return OHLCVValidator.validate(df, strict=strict)

