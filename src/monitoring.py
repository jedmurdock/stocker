"""
Monitoring and metrics tracking for the trading system.
Tracks errors, performance, and trading activity.
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json
from pathlib import Path


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: datetime
    errors_count: int
    warnings_count: int
    trades_executed: int
    signals_generated: int
    api_calls: int
    avg_response_time_ms: float


class MonitoringSystem:
    """
    Central monitoring system for tracking application health and metrics.
    Thread-safe for concurrent access.
    """
    
    def __init__(self):
        """Initialize monitoring system"""
        self.errors: Dict[str, List[Dict]] = defaultdict(list)
        self.warnings: Dict[str, List[Dict]] = defaultdict(list)
        self.metrics: Dict[str, int] = defaultdict(int)
        self.timings: Dict[str, List[float]] = defaultdict(list)
        self.start_time = datetime.now()
    
    def record_error(self, category: str, error: Exception, context: Optional[Dict] = None):
        """
        Record an error occurrence.
        
        Args:
            category: Error category (e.g., 'data_fetch', 'strategy', 'broker')
            error: The exception that occurred
            context: Additional context information
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        self.errors[category].append(error_entry)
        self.metrics[f'errors_{category}'] += 1
        self.metrics['total_errors'] += 1
    
    def record_warning(self, category: str, message: str, context: Optional[Dict] = None):
        """
        Record a warning.
        
        Args:
            category: Warning category
            message: Warning message
            context: Additional context
        """
        warning_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'context': context or {}
        }
        self.warnings[category].append(warning_entry)
        self.metrics[f'warnings_{category}'] += 1
        self.metrics['total_warnings'] += 1
    
    def record_metric(self, name: str, value: int = 1):
        """
        Record a metric increment.
        
        Args:
            name: Metric name
            value: Value to add (default 1)
        """
        self.metrics[name] += value
    
    def record_timing(self, operation: str, duration_ms: float):
        """
        Record operation timing.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
        """
        self.timings[operation].append(duration_ms)
        self.metrics[f'{operation}_count'] += 1
    
    def get_error_rate(self, category: Optional[str] = None) -> float:
        """
        Get error rate (errors per minute).
        
        Args:
            category: Specific category or None for all
            
        Returns:
            Errors per minute
        """
        runtime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        if runtime_minutes < 0.01:  # Avoid division by zero
            runtime_minutes = 0.01
        
        if category:
            error_count = self.metrics.get(f'errors_{category}', 0)
        else:
            error_count = self.metrics.get('total_errors', 0)
        
        return error_count / runtime_minutes
    
    def get_avg_timing(self, operation: str) -> float:
        """
        Get average timing for an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Average duration in milliseconds
        """
        timings = self.timings.get(operation, [])
        return sum(timings) / len(timings) if timings else 0.0
    
    def get_snapshot(self) -> MetricSnapshot:
        """Get current metrics snapshot"""
        return MetricSnapshot(
            timestamp=datetime.now(),
            errors_count=self.metrics.get('total_errors', 0),
            warnings_count=self.metrics.get('total_warnings', 0),
            trades_executed=self.metrics.get('trades_executed', 0),
            signals_generated=self.metrics.get('signals_generated', 0),
            api_calls=self.metrics.get('api_calls', 0),
            avg_response_time_ms=self.get_avg_timing('api_call')
        )
    
    def get_summary(self) -> Dict:
        """
        Get a summary of all metrics.
        
        Returns:
            Dictionary with metric summaries
        """
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': runtime,
            'errors': {
                'total': self.metrics.get('total_errors', 0),
                'by_category': {k: len(v) for k, v in self.errors.items()},
                'rate_per_minute': self.get_error_rate()
            },
            'warnings': {
                'total': self.metrics.get('total_warnings', 0),
                'by_category': {k: len(v) for k, v in self.warnings.items()}
            },
            'metrics': dict(self.metrics),
            'timings': {
                op: {
                    'count': len(times),
                    'avg_ms': sum(times) / len(times) if times else 0,
                    'min_ms': min(times) if times else 0,
                    'max_ms': max(times) if times else 0
                }
                for op, times in self.timings.items()
            }
        }
    
    def save_report(self, filepath: str):
        """
        Save monitoring report to file.
        
        Args:
            filepath: Path to save report
        """
        report = self.get_summary()
        report['timestamp'] = datetime.now().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
    
    def reset(self):
        """Reset all metrics and errors"""
        self.errors.clear()
        self.warnings.clear()
        self.metrics.clear()
        self.timings.clear()
        self.start_time = datetime.now()


# Global monitoring instance
_monitor = MonitoringSystem()


def get_monitor() -> MonitoringSystem:
    """Get the global monitoring instance"""
    return _monitor

