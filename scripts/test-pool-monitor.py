#!/usr/bin/env python3
"""
Test script for Database Connection Pool Monitor
Simulates various database usage scenarios to test pool monitoring
"""

import asyncio
import time
import threading
from contextlib import contextmanager
from app.db.session import get_db_session_sync
from app.db.pool_monitor import get_pool_monitor, ConnectionMonitor, check_pool_health
from app.main import app
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_pool_metrics():
    """Test basic pool metrics retrieval."""
    print("🧪 Testing basic pool metrics...")
    
    monitor = get_pool_monitor()
    metrics = monitor.get_pool_metrics()
    
    if metrics:
        print(f"✅ Pool metrics retrieved successfully:")
        print(f"   Pool Size: {metrics.pool_size}")
        print(f"   Checked Out: {metrics.checked_out}")
        print(f"   Utilization: {metrics.utilization_percent:.1f}%")
        print(f"   Total Connections: {metrics.total_connections}")
        return True
    else:
        print("❌ Failed to retrieve pool metrics")
        return False

def test_pool_health_check():
    """Test pool health check API."""
    print("\n🧪 Testing pool health check...")
    
    health = check_pool_health()
    
    if "error" in health:
        print(f"❌ Pool health check failed: {health['error']}")
        return False
    else:
        print(f"✅ Pool health check passed:")
        print(f"   Status: {health['status']}")
        print(f"   Current Utilization: {health['current']['utilization_percent']}%")
        print(f"   Recommendations: {len(health['recommendations'])} items")
        return True

def test_connection_monitor():
    """Test the ConnectionMonitor context manager."""
    print("\n🧪 Testing ConnectionMonitor context manager...")
    
    try:
        with ConnectionMonitor("test_operation"):
            # Simulate some database work
            db = get_db_session_sync()
            try:
                time.sleep(0.1)  # Simulate work
            finally:
                db.close()
                
        print("✅ ConnectionMonitor worked successfully")
        return True
    except Exception as e:
        print(f"❌ ConnectionMonitor failed: {e}")
        return False

def simulate_high_usage():
    """Simulate high database usage to test pool monitoring."""
    print("\n🧪 Simulating high database usage...")
    
    def db_worker(worker_id, duration=2):
        """Worker function that holds database connections."""
        try:
            with ConnectionMonitor(f"worker_{worker_id}"):
                db = get_db_session_sync()
                try:
                    # Simulate long-running database work
                    time.sleep(duration)
                finally:
                    db.close()
                    
        except Exception as e:
            logger.error(f"Worker {worker_id} failed: {e}")
    
    # Create multiple workers to stress test the pool
    threads = []
    num_workers = 3  # Start with 3 workers to avoid overwhelming the pool
    
    print(f"   Starting {num_workers} concurrent database workers...")
    
    for i in range(num_workers):
        thread = threading.Thread(target=db_worker, args=(i, 1))
        threads.append(thread)
        thread.start()
    
    # Monitor pool usage during high load
    start_time = time.time()
    max_utilization = 0
    
    while any(t.is_alive() for t in threads):
        monitor = get_pool_monitor()
        metrics = monitor.get_pool_metrics()
        
        if metrics:
            max_utilization = max(max_utilization, metrics.utilization_percent)
            print(f"   ⏱️  Pool utilization: {metrics.utilization_percent:.1f}% "
                  f"(checked out: {metrics.checked_out})")
            
        time.sleep(0.5)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    duration = time.time() - start_time
    print(f"✅ High usage simulation completed in {duration:.1f}s")
    print(f"   Maximum utilization reached: {max_utilization:.1f}%")
    
    return max_utilization > 0

def test_pool_alerts():
    """Test pool alert system."""
    print("\n🧪 Testing pool alert system...")
    
    monitor = get_pool_monitor()
    
    # Reset alert state
    monitor.last_alert_time = None
    
    # Check current metrics
    metrics = monitor.get_pool_metrics()
    
    if metrics:
        print(f"   Current utilization: {metrics.utilization_percent:.1f}%")
        
        if metrics.is_critical():
            print("⚠️  Pool is in critical state - alerts should be triggered")
        elif metrics.is_warning():
            print("⚠️  Pool is in warning state")
        else:
            print("✅ Pool is in healthy state")
            
        return True
    else:
        print("❌ Could not get metrics for alert testing")
        return False

def main():
    """Run all pool monitor tests."""
    print("🔍 Database Connection Pool Monitor Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Pool Metrics", test_basic_pool_metrics),
        ("Pool Health Check", test_pool_health_check),
        ("Connection Monitor", test_connection_monitor),
        ("High Usage Simulation", simulate_high_usage),
        ("Pool Alerts", test_pool_alerts),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Pool monitoring is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")
    
    # Final pool status
    print("\n📋 Final Pool Status:")
    get_pool_monitor().log_pool_status()

if __name__ == "__main__":
    main() 