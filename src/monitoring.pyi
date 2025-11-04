"""Type stubs for monitoring module"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MetricSnapshot:
    timestamp: datetime
    errors_count: int
    warnings_count: int
    trades_executed: int
    signals_generated: int
    api_calls: int
    avg_response_time_ms: float

class MonitoringSystem:
    errors: Dict[str, List[Dict]]
    warnings: Dict[str, List[Dict]]
    metrics: Dict[str, int]
    timings: Dict[str, List[float]]
    start_time: datetime
    
    def __init__(self) -> None: ...
    
    def record_error(self, category: str, error: Exception, context: Optional[Dict] = None) -> None: ...
    
    def record_warning(self, category: str, message: str, context: Optional[Dict] = None) -> None: ...
    
    def record_metric(self, name: str, value: int = 1) -> None: ...
    
    def record_timing(self, operation: str, duration_ms: float) -> None: ...
    
    def get_error_rate(self, category: Optional[str] = None) -> float: ...
    
    def get_avg_timing(self, operation: str) -> float: ...
    
    def get_snapshot(self) -> MetricSnapshot: ...
    
    def get_summary(self) -> Dict: ...
    
    def save_report(self, filepath: str) -> None: ...
    
    def reset(self) -> None: ...

def get_monitor() -> MonitoringSystem: ...

