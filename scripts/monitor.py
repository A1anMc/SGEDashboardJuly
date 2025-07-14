#!/usr/bin/env python3
"""
Comprehensive monitoring script for the SGE Dashboard.
This script checks various components of the system and reports their status.
"""

import os
import sys
import json
import time
import psutil
import requests
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()

class SystemMonitor:
    def __init__(self, backend_url: str = None, check_interval: int = 60):
        self.backend_url = backend_url or "http://localhost:8000"
        self.check_interval = check_interval
        self.engine = create_engine(settings.DATABASE_URL)
        
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "open_files": len(psutil.Process().open_files()),
            "connections": len(psutil.Process().connections()),
        }
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and health."""
        try:
            with self.engine.connect() as conn:
                # Check connection
                conn.execute(text("SELECT 1"))
                
                # Get connection pool stats
                pool_info = {
                    "pool_size": self.engine.pool.size(),
                    "checkedin": self.engine.pool.checkedin(),
                    "overflow": self.engine.pool.overflow(),
                    "checkedout": self.engine.pool.checkedout(),
                }
                
                # Get PostgreSQL specific stats
                try:
                    result = conn.execute(text("""
                        SELECT datname, numbackends, xact_commit, xact_rollback, 
                               blks_read, blks_hit, tup_returned, tup_fetched,
                               tup_inserted, tup_updated, tup_deleted
                        FROM pg_stat_database 
                        WHERE datname = current_database()
                    """))
                    row = result.fetchone()
                    if row:
                        pg_stats = dict(zip(result.keys(), row))
                    else:
                        pg_stats = {}
                except Exception as e:
                    logger.warning(f"Could not fetch PostgreSQL stats: {e}")
                    pg_stats = {}
                
                return {
                    "status": "healthy",
                    "pool_info": pool_info,
                    "pg_stats": pg_stats
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_api_endpoints(self) -> List[Dict[str, Any]]:
        """Check key API endpoints."""
        endpoints = [
            "/health",
            "/api/v1/grants",
            "/api/v1/tasks",
            "/api/v1/projects"
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    timeout=30,  # Increased timeout for production
                    headers={"User-Agent": "SGE-Monitor/1.0"}
                )
                duration = (time.time() - start_time) * 1000  # ms
                
                results.append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time_ms": round(duration, 2),
                    "healthy": response.status_code < 500
                })
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "error": str(e),
                    "healthy": False
                })
        
        return results
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all system checks and return results."""
        timestamp = datetime.utcnow().isoformat()
        
        results = {
            "timestamp": timestamp,
            "environment": settings.ENV,
            "system_resources": self.check_system_resources(),
            "database": self.check_database(),
            "api_endpoints": self.check_api_endpoints()
        }
        
        # Calculate overall health
        is_healthy = (
            results["database"]["status"] == "healthy" and
            all(endpoint["healthy"] for endpoint in results["api_endpoints"]) and
            results["system_resources"]["cpu_percent"] < 90 and
            results["system_resources"]["memory_percent"] < 90
        )
        
        results["overall_health"] = "healthy" if is_healthy else "degraded"
        return results
    
    def monitor_continuously(self):
        """Run monitoring checks continuously."""
        while True:
            try:
                results = self.run_checks()
                
                # Log results
                if results["overall_health"] == "healthy":
                    logger.info("System health check passed", extra={"monitor_results": results})
                else:
                    logger.warning("System health check failed", extra={"monitor_results": results})
                
                # Write to file
                with open("logs/monitor.json", "a") as f:
                    f.write(json.dumps(results) + "\n")
                    
            except Exception as e:
                logger.error(f"Monitoring check failed: {str(e)}")
            
            time.sleep(self.check_interval)

def main():
    parser = argparse.ArgumentParser(description="SGE Dashboard System Monitor")
    parser.add_argument("--backend-url", help="Backend API URL", default="http://localhost:8000")
    parser.add_argument("--interval", type=int, help="Check interval in seconds", default=60)
    parser.add_argument("--once", action="store_true", help="Run checks once and exit")
    args = parser.parse_args()
    
    monitor = SystemMonitor(args.backend_url, args.interval)
    
    if args.once:
        results = monitor.run_checks()
        print(json.dumps(results, indent=2))
    else:
        logger.info(f"Starting continuous monitoring (interval: {args.interval}s)")
        monitor.monitor_continuously()

if __name__ == "__main__":
    main() 