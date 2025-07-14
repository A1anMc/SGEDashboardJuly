#!/usr/bin/env python3
"""
Test script for Robust API Client
Tests retry logic, circuit breaker, and connection monitoring
"""

import time
from app.core.api_client import (
    APIClient, 
    RetryConfig, 
    get_api_client,
    get_scraper_client,
    get_all_client_metrics,
    health_check_all_clients
)
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_request():
    """Test basic API request functionality."""
    print("🧪 Testing basic API request...")
    
    client = APIClient(base_url="https://httpbin.org")
    response = client.get("/get")
    
    if response.success:
        print(f"✅ Basic request successful: {response.status_code}")
        print(f"   Response time: {response.elapsed:.3f}s")
        print(f"   URL: {response.url}")
        return True
    else:
        print(f"❌ Basic request failed: {response.status_code} - {response.error}")
        return False

def test_retry_logic():
    """Test retry logic with simulated failures."""
    print("\n🧪 Testing retry logic...")
    
    # Use httpbin's status endpoint to simulate failures
    client = APIClient(base_url="https://httpbin.org")
    
    # Test with 500 status (should retry)
    response = client.get("/status/500")
    
    if response.attempt > 1:
        print(f"✅ Retry logic working: {response.attempt} attempts made")
        print(f"   Final status: {response.status_code}")
        return True
    else:
        print(f"❌ Retry logic not working: only {response.attempt} attempt")
        return False

def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\n🧪 Testing circuit breaker...")
    
    # Create client with aggressive retry settings
    retry_config = RetryConfig(max_retries=2, initial_delay=0.1)
    client = APIClient(base_url="https://httpbin.org", retry_config=retry_config)
    
    # Make multiple failing requests to trigger circuit breaker
    for i in range(6):
        response = client.get("/status/500")
        print(f"   Request {i+1}: {response.status_code}")
        
        if response.error == "Circuit breaker is open":
            print("✅ Circuit breaker triggered successfully")
            return True
    
    print("❌ Circuit breaker not triggered")
    return False

def test_domain_validation():
    """Test domain validation for external requests."""
    print("\n🧪 Testing domain validation...")
    
    client = APIClient()
    
    # Test allowed domain
    response = client.get("https://httpbin.org/get")
    if response.status_code == 403:
        print("❌ Allowed domain was blocked")
        return False
    
    # Test blocked domain
    response = client.get("https://malicious-site.com/api")
    if response.status_code == 403:
        print("✅ Blocked domain was properly rejected")
        return True
    else:
        print(f"❌ Blocked domain was allowed: {response.status_code}")
        return False

def test_scraper_client():
    """Test scraper-specific client configuration."""
    print("\n🧪 Testing scraper client configuration...")
    
    try:
        # Test with business.gov.au scraper
        client = get_scraper_client("business.gov.au")
        
        print(f"✅ Scraper client created for business.gov.au")
        print(f"   Base URL: {client.base_url}")
        print(f"   Timeout: {client.timeout}")
        print(f"   Max retries: {client.retry_config.max_retries}")
        
        # Test basic request
        response = client.get("/")
        print(f"   Test request status: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Scraper client creation failed: {e}")
        return False

def test_metrics_collection():
    """Test API client metrics collection."""
    print("\n🧪 Testing metrics collection...")
    
    client = APIClient(base_url="https://httpbin.org")
    
    # Make some requests
    client.get("/get")
    client.get("/status/404")  # This should fail
    client.post("/post", data={"test": "data"})
    
    metrics = client.get_metrics()
    
    if metrics["total_requests"] >= 3:
        print("✅ Metrics collection working:")
        print(f"   Total requests: {metrics['total_requests']}")
        print(f"   Successful: {metrics['successful_requests']}")
        print(f"   Failed: {metrics['failed_requests']}")
        print(f"   Success rate: {metrics['success_rate']}%")
        print(f"   Avg response time: {metrics['avg_response_time']}s")
        return True
    else:
        print(f"❌ Metrics not collected properly: {metrics}")
        return False

def test_global_client_management():
    """Test global client management functions."""
    print("\n🧪 Testing global client management...")
    
    # Create some clients
    client1 = get_api_client("test_service_1", "https://httpbin.org")
    client2 = get_api_client("test_service_2", "https://httpbin.org")
    
    # Make some requests
    client1.get("/get")
    client2.get("/ip")
    
    # Get all metrics
    all_metrics = get_all_client_metrics()
    
    if len(all_metrics) >= 2:
        print("✅ Global client management working:")
        for service_name, metrics in all_metrics.items():
            print(f"   {service_name}: {metrics['total_requests']} requests")
        return True
    else:
        print(f"❌ Global client management not working: {all_metrics}")
        return False

def test_health_checks():
    """Test health check functionality."""
    print("\n🧪 Testing health checks...")
    
    client = APIClient(base_url="https://httpbin.org")
    health = client.health_check()
    
    if health["status"] in ["healthy", "unhealthy"]:
        print("✅ Health check working:")
        print(f"   Status: {health['status']}")
        print(f"   Base URL: {health['base_url']}")
        print(f"   Circuit breaker: {health['circuit_breaker_open']}")
        return True
    else:
        print(f"❌ Health check not working: {health}")
        return False

def test_timeout_handling():
    """Test timeout handling."""
    print("\n🧪 Testing timeout handling...")
    
    client = APIClient(base_url="https://httpbin.org", timeout=1.0)
    
    # Use httpbin's delay endpoint to simulate slow response
    start_time = time.time()
    response = client.get("/delay/3")  # 3-second delay
    elapsed = time.time() - start_time
    
    if elapsed < 5.0 and not response.success:  # Should timeout before 5 seconds
        print(f"✅ Timeout handled correctly: {elapsed:.1f}s")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.error}")
        return True
    else:
        print(f"❌ Timeout not handled properly: {elapsed:.1f}s, success: {response.success}")
        return False

def main():
    """Run all API client tests."""
    print("🔍 Robust API Client Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Request", test_basic_request),
        ("Retry Logic", test_retry_logic),
        ("Circuit Breaker", test_circuit_breaker),
        ("Domain Validation", test_domain_validation),
        ("Scraper Client", test_scraper_client),
        ("Metrics Collection", test_metrics_collection),
        ("Global Client Management", test_global_client_management),
        ("Health Checks", test_health_checks),
        ("Timeout Handling", test_timeout_handling),
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
        print("🎉 All tests passed! API client is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")
    
    # Show final metrics
    print("\n📋 Final API Client Metrics:")
    all_metrics = get_all_client_metrics()
    for service_name, metrics in all_metrics.items():
        print(f"  {service_name}:")
        print(f"    Total requests: {metrics['total_requests']}")
        print(f"    Success rate: {metrics['success_rate']}%")
        print(f"    Avg response time: {metrics['avg_response_time']}s")

if __name__ == "__main__":
    main() 