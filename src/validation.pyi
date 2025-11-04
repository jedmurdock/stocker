"""Type stubs for validation module"""
import pandas as pd
from typing import List
from dataclasses import dataclass

@dataclass
class ValidationError:
    field: str
    error_type: str
    message: str

class OHLCVValidator:
    REQUIRED_COLUMNS: List[str]
    
    @classmethod
    def validate(cls, df: pd.DataFrame, strict: bool = True) -> List[ValidationError]: ...
    
    @classmethod
    def is_valid(cls, df: pd.DataFrame) -> bool: ...

def validate_ohlcv(df: pd.DataFrame, strict: bool = True) -> List[ValidationError]: ...

