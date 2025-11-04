"""
Tests for monitoring module.
"""
import pytest
from monitoring import MonitoringSystem, get_monitor, MetricSnapshot
import time
import tempfile
import json


class TestMonitoringSystem:
    """Test monitoring functionality"""
    
    def setup_method(self):
        """Reset monitor between tests"""
        monitor = MonitoringSystem()
        monitor.reset()
    
    def test_monitoring_initialization(self):
        """Test monitor initializes correctly"""
        monitor = MonitoringSystem()
        assert monitor.metrics['total_errors'] == 0
        assert monitor.metrics['total_warnings'] == 0
    
    def test_record_error(self):
        """Test recording errors"""
        monitor = MonitoringSystem()
        error = ValueError("Test error")
        
        monitor.record_error("test_category", error, {"key": "value"})
        
        assert monitor.metrics['total_errors'] == 1
        assert monitor.metrics['errors_test_category'] == 1
        assert len(monitor.errors['test_category']) == 1
        
        error_entry = monitor.errors['test_category'][0]
        assert error_entry['error_type'] == 'ValueError'
        assert error_entry['message'] == 'Test error'
        assert error_entry['context']['key'] == 'value'
    
    def test_record_warning(self):
        """Test recording warnings"""
        monitor = MonitoringSystem()
        
        monitor.record_warning("test_category", "Test warning", {"info": "test"})
        
        assert monitor.metrics['total_warnings'] == 1
        assert monitor.metrics['warnings_test_category'] == 1
        assert len(monitor.warnings['test_category']) == 1
    
    def test_record_metric(self):
        """Test recording metrics"""
        monitor = MonitoringSystem()
        
        monitor.record_metric("test_metric", 5)
        assert monitor.metrics['test_metric'] == 5
        
        monitor.record_metric("test_metric", 3)
        assert monitor.metrics['test_metric'] == 8
    
    def test_record_timing(self):
        """Test recording operation timings"""
        monitor = MonitoringSystem()
        
        monitor.record_timing("test_op", 100.5)
        monitor.record_timing("test_op", 200.5)
        
        assert len(monitor.timings['test_op']) == 2
        avg = monitor.get_avg_timing("test_op")
        assert avg == 150.5
    
    def test_get_error_rate(self):
        """Test error rate calculation"""
        monitor = MonitoringSystem()
        
        # Record some errors
        for i in range(5):
            monitor.record_error("test", ValueError(f"Error {i}"))
        
        rate = monitor.get_error_rate()
        assert rate >= 0  # Should be positive
    
    def test_get_snapshot(self):
        """Test getting metric snapshot"""
        monitor = MonitoringSystem()
        
        monitor.record_error("test", ValueError("Error"))
        monitor.record_warning("test", "Warning")
        monitor.record_metric("trades_executed", 10)
        
        snapshot = monitor.get_snapshot()
        
        assert isinstance(snapshot, MetricSnapshot)
        assert snapshot.errors_count == 1
        assert snapshot.warnings_count == 1
        assert snapshot.trades_executed == 10
    
    def test_get_summary(self):
        """Test getting full summary"""
        monitor = MonitoringSystem()
        
        monitor.record_error("data_fetch", ValueError("Error"))
        monitor.record_metric("api_calls", 5)
        monitor.record_timing("fetch_data", 123.4)
        
        summary = monitor.get_summary()
        
        assert 'errors' in summary
        assert 'metrics' in summary
        assert 'timings' in summary
        assert summary['errors']['total'] == 1
        assert summary['metrics']['api_calls'] == 5
    
    def test_save_report(self):
        """Test saving monitoring report"""
        monitor = MonitoringSystem()
        
        monitor.record_error("test", ValueError("Error"))
        monitor.record_metric("test_metric", 42)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            monitor.save_report(filepath)
            
            # Read back and verify
            with open(filepath, 'r') as f:
                report = json.load(f)
            
            assert 'errors' in report
            assert 'metrics' in report
            assert report['errors']['total'] == 1
            assert report['metrics']['test_metric'] == 42
        finally:
            import os
            os.unlink(filepath)
    
    def test_reset(self):
        """Test resetting metrics"""
        monitor = MonitoringSystem()
        
        monitor.record_error("test", ValueError("Error"))
        monitor.record_metric("test", 5)
        
        assert monitor.metrics['total_errors'] == 1
        
        monitor.reset()
        
        assert monitor.metrics['total_errors'] == 0
        assert len(monitor.errors) == 0
    
    def test_global_monitor(self):
        """Test global monitor instance"""
        monitor = get_monitor()
        assert monitor is not None
        assert isinstance(monitor, MonitoringSystem)
        
        # Should return same instance
        monitor2 = get_monitor()
        assert monitor is monitor2

