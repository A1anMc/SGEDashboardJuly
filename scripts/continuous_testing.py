#!/usr/bin/env python3
"""
Continuous Testing Script for SGE Dashboard
Monitors system health, runs tests, and catches issues before they become problems.
"""

import asyncio
import subprocess
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/continuous_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousTestRunner:
    def __init__(self, interval: int = 300):  # 5 minutes default
        self.interval = interval
        self.last_results = {}
        self.failure_count = 0
        self.max_failures = 3
        
    def run_command(self, command: List[str], timeout: int = 60) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, f"Error running command: {str(e)}"
    
    def test_backend_startup(self) -> Dict[str, any]:
        """Test if the backend can start without errors."""
        logger.info("Testing backend startup...")
        
        # Test configuration loading
        success, output = self.run_command([
            sys.executable, "-c", 
            "from app.main import create_app; app = create_app(); print('Backend startup test passed')"
        ])
        
        return {
            "name": "Backend Startup",
            "success": success,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_database_connection(self) -> Dict[str, any]:
        """Test database connectivity."""
        logger.info("Testing database connection...")
        
        success, output = self.run_command([
            sys.executable, "-c",
            "from app.db.session import get_db_session; db = next(get_db_session()); print('Database connection test passed')"
        ])
        
        return {
            "name": "Database Connection",
            "success": success,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_api_endpoints(self) -> Dict[str, any]:
        """Test API endpoints if backend is running."""
        logger.info("Testing API endpoints...")
        
        endpoints = [
            "http://localhost:8000/api/v1/health",
            "http://localhost:8000/api/v1/grants",
            "http://localhost:8000/api/v1/projects",
            "http://localhost:8000/api/v1/tasks",
            "http://localhost:8000/api/v1/users"
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                results.append({
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "success": response.status_code in [200, 307]  # 307 is redirect
                })
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "status": "error",
                    "success": False,
                    "error": str(e)
                })
        
        success = all(r["success"] for r in results)
        return {
            "name": "API Endpoints",
            "success": success,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_cors_configuration(self) -> Dict[str, any]:
        """Test CORS configuration."""
        logger.info("Testing CORS configuration...")
        
        try:
            response = requests.get("http://localhost:8000/api/debug/cors", timeout=10)
            if response.status_code == 200:
                cors_config = response.json()
                
                # Check if production domains are included
                origins = cors_config.get("cors_origins", [])
                has_production = any("sge-dashboard-web.onrender.com" in origin for origin in origins)
                
                return {
                    "name": "CORS Configuration",
                    "success": has_production,
                    "config": cors_config,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "name": "CORS Configuration",
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "name": "CORS Configuration",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_pytest(self) -> Dict[str, any]:
        """Run pytest on the test suite."""
        logger.info("Running pytest...")
        
        success, output = self.run_command([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"
        ], timeout=120)
        
        return {
            "name": "PyTest Suite",
            "success": success,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_frontend_build(self) -> Dict[str, any]:
        """Test frontend build process."""
        logger.info("Testing frontend build...")
        
        success, output = self.run_command([
            "npm", "run", "build"
        ], timeout=180)
        
        return {
            "name": "Frontend Build",
            "success": success,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_all_tests(self) -> Dict[str, any]:
        """Run all tests and return results."""
        logger.info("Starting comprehensive test run...")
        
        tests = [
            self.test_backend_startup,
            self.test_database_connection,
            self.test_api_endpoints,
            self.test_cors_configuration,
            self.run_pytest,
            # self.test_frontend_build  # Commented out as it's time-consuming
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                
                if result["success"]:
                    logger.info(f"✅ {result['name']}: PASSED")
                else:
                    logger.error(f"❌ {result['name']}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test.__name__}: ERROR - {str(e)}")
                results.append({
                    "name": test.__name__,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Calculate overall success
        passed = sum(1 for r in results if r["success"])
        total = len(results)
        overall_success = passed == total
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "overall_success": overall_success,
            "passed": passed,
            "total": total,
            "results": results
        }
        
        # Update failure count
        if overall_success:
            self.failure_count = 0
        else:
            self.failure_count += 1
        
        return summary
    
    def save_results(self, results: Dict[str, any]) -> None:
        """Save test results to file."""
        results_file = Path("logs/test_results.json")
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
    
    def send_alert(self, results: Dict[str, any]) -> None:
        """Send alert if tests are failing consistently."""
        if self.failure_count >= self.max_failures:
            logger.critical(f"🚨 ALERT: Tests have failed {self.failure_count} times in a row!")
            logger.critical("System may be in a degraded state. Manual intervention required.")
            
            # Here you could integrate with alerting systems like:
            # - Email notifications
            # - Slack webhooks
            # - PagerDuty
            # - etc.
    
    async def run_continuous(self) -> None:
        """Run tests continuously at specified interval."""
        logger.info(f"Starting continuous testing with {self.interval}s interval...")
        
        while True:
            try:
                results = self.run_all_tests()
                self.save_results(results)
                
                if results["overall_success"]:
                    logger.info(f"🎉 All tests passed! ({results['passed']}/{results['total']})")
                else:
                    logger.warning(f"⚠️ Some tests failed ({results['passed']}/{results['total']})")
                    self.send_alert(results)
                
                # Wait for next interval
                logger.info(f"Waiting {self.interval}s until next test run...")
                await asyncio.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("Continuous testing stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous testing: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous Testing for SGE Dashboard")
    parser.add_argument("--interval", type=int, default=300, help="Test interval in seconds (default: 300)")
    parser.add_argument("--once", action="store_true", help="Run tests once and exit")
    
    args = parser.parse_args()
    
    runner = ContinuousTestRunner(interval=args.interval)
    
    if args.once:
        results = runner.run_all_tests()
        runner.save_results(results)
        
        if results["overall_success"]:
            logger.info("🎉 All tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some tests failed!")
            sys.exit(1)
    else:
        asyncio.run(runner.run_continuous())

if __name__ == "__main__":
    main() 