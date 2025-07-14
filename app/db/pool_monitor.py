"""
Database Connection Pool Monitor
Monitors SQLAlchemy connection pool usage to prevent exhaustion
"""
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from threading import Lock
from sqlalchemy.pool import QueuePool
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PoolMetrics:
    """Connection pool metrics at a point in time."""
    timestamp: datetime
    pool_size: int
    checked_out: int
    overflow: int
    checked_in: int
    total_connections: int
    utilization_percent: float
    overflow_utilization_percent: float
    
    def is_critical(self) -> bool:
        """Check if pool utilization is in critical range."""
        return self.utilization_percent > 80.0
    
    def is_warning(self) -> bool:
        """Check if pool utilization is in warning range."""
        return self.utilization_percent > 60.0

class DatabasePoolMonitor:
    """Monitors database connection pool usage and provides metrics."""
    
    def __init__(self, engine=None, alert_threshold: float = 80.0):
        self.engine = engine
        self.alert_threshold = alert_threshold
        self.metrics_history: List[PoolMetrics] = []
        self.lock = Lock()
        self.last_alert_time: Optional[datetime] = None
        self.alert_cooldown = timedelta(minutes=5)  # Don't spam alerts
        
    def set_engine(self, engine):
        """Set the database engine to monitor."""
        self.engine = engine
        
    def get_pool_metrics(self) -> Optional[PoolMetrics]:
        """Get current connection pool metrics."""
        if not self.engine or not hasattr(self.engine, 'pool'):
            return None
            
        try:
            pool = self.engine.pool
            if not isinstance(pool, QueuePool):
                logger.warning(f"Pool monitoring not supported for {type(pool)}")
                return None
                
            # Get pool statistics
            pool_size = pool.size()
            checked_out = pool.checkedout()
            overflow = pool.overflow()
            checked_in = pool.checkedin()
            total_connections = checked_out + checked_in
            
            # Calculate utilization percentages
            max_pool_size = settings.DATABASE_POOL_SIZE
            max_overflow = settings.DATABASE_MAX_OVERFLOW
            max_total = max_pool_size + max_overflow
            
            utilization_percent = (checked_out / max_pool_size) * 100 if max_pool_size > 0 else 0
            overflow_utilization_percent = (overflow / max_overflow) * 100 if max_overflow > 0 else 0
            
            metrics = PoolMetrics(
                timestamp=datetime.now(),
                pool_size=pool_size,
                checked_out=checked_out,
                overflow=overflow,
                checked_in=checked_in,
                total_connections=total_connections,
                utilization_percent=utilization_percent,
                overflow_utilization_percent=overflow_utilization_percent
            )
            
            # Store metrics history (keep last 100 entries)
            with self.lock:
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)
                    
            # Check for alerts
            self._check_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting pool metrics: {e}")
            return None
    
    def _check_alerts(self, metrics: PoolMetrics):
        """Check if alerts should be sent based on current metrics."""
        if not metrics.is_critical():
            return
            
        now = datetime.now()
        
        # Check cooldown period
        if (self.last_alert_time and 
            now - self.last_alert_time < self.alert_cooldown):
            return
            
        # Send alert
        self.last_alert_time = now
        logger.warning(
            f"🚨 DATABASE POOL ALERT: High utilization detected!\n"
            f"Pool Utilization: {metrics.utilization_percent:.1f}%\n"
            f"Checked Out: {metrics.checked_out}/{settings.DATABASE_POOL_SIZE}\n"
            f"Overflow: {metrics.overflow}/{settings.DATABASE_MAX_OVERFLOW}\n"
            f"Total Connections: {metrics.total_connections}"
        )
        
        # Log recommendations
        if metrics.utilization_percent > 90:
            logger.error("🔴 CRITICAL: Pool near exhaustion - consider increasing pool size")
        elif metrics.overflow > 0:
            logger.warning("🟡 WARNING: Using overflow connections - monitor closely")
    
    def get_pool_summary(self) -> Dict:
        """Get a summary of pool health and recent metrics."""
        current_metrics = self.get_pool_metrics()
        
        if not current_metrics:
            return {"error": "Unable to get pool metrics"}
            
        # Calculate averages from recent history
        recent_metrics = [m for m in self.metrics_history 
                         if m.timestamp > datetime.now() - timedelta(minutes=5)]
        
        if recent_metrics:
            avg_utilization = sum(m.utilization_percent for m in recent_metrics) / len(recent_metrics)
            max_utilization = max(m.utilization_percent for m in recent_metrics)
            avg_checked_out = sum(m.checked_out for m in recent_metrics) / len(recent_metrics)
        else:
            avg_utilization = current_metrics.utilization_percent
            max_utilization = current_metrics.utilization_percent
            avg_checked_out = current_metrics.checked_out
            
        return {
            "status": "healthy" if not current_metrics.is_critical() else "critical",
            "current": {
                "pool_size": current_metrics.pool_size,
                "checked_out": current_metrics.checked_out,
                "overflow": current_metrics.overflow,
                "utilization_percent": round(current_metrics.utilization_percent, 1),
                "total_connections": current_metrics.total_connections
            },
            "recent_5min": {
                "avg_utilization_percent": round(avg_utilization, 1),
                "max_utilization_percent": round(max_utilization, 1),
                "avg_checked_out": round(avg_checked_out, 1)
            },
            "configuration": {
                "max_pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
                "pool_recycle": settings.DATABASE_POOL_RECYCLE
            },
            "recommendations": self._get_recommendations(current_metrics)
        }
    
    def _get_recommendations(self, metrics: PoolMetrics) -> List[str]:
        """Get recommendations based on current metrics."""
        recommendations = []
        
        if metrics.utilization_percent > 90:
            recommendations.append("🔴 CRITICAL: Increase DATABASE_POOL_SIZE immediately")
            recommendations.append("Consider scaling down concurrent scraper operations")
            
        elif metrics.utilization_percent > 80:
            recommendations.append("🟡 WARNING: High utilization - monitor closely")
            recommendations.append("Consider increasing DATABASE_POOL_SIZE")
            
        elif metrics.overflow > 0:
            recommendations.append("🟡 Using overflow connections - consider increasing pool size")
            
        if metrics.utilization_percent > 60:
            recommendations.append("Monitor scraper scheduling to avoid peak usage")
            recommendations.append("Consider connection pooling optimizations")
            
        if not recommendations:
            recommendations.append("✅ Pool utilization is healthy")
            
        return recommendations
    
    def get_metrics_history(self, minutes: int = 30) -> List[PoolMetrics]:
        """Get metrics history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            return [m for m in self.metrics_history if m.timestamp > cutoff_time]
    
    def reset_metrics_history(self):
        """Reset the metrics history."""
        with self.lock:
            self.metrics_history.clear()
            
    def log_pool_status(self, level: str = "info"):
        """Log current pool status."""
        summary = self.get_pool_summary()
        
        if "error" in summary:
            logger.error(f"Pool monitoring error: {summary['error']}")
            return
            
        status = summary["status"]
        current = summary["current"]
        
        log_func = getattr(logger, level, logger.info)
        log_func(
            f"Database Pool Status: {status.upper()}\n"
            f"Utilization: {current['utilization_percent']}% "
            f"({current['checked_out']}/{current['pool_size']})\n"
            f"Overflow: {current['overflow']}, "
            f"Total Connections: {current['total_connections']}"
        )

# Global monitor instance
_pool_monitor: Optional[DatabasePoolMonitor] = None

def get_pool_monitor() -> DatabasePoolMonitor:
    """Get the global pool monitor instance."""
    global _pool_monitor
    if _pool_monitor is None:
        _pool_monitor = DatabasePoolMonitor()
    return _pool_monitor

def initialize_pool_monitor(engine):
    """Initialize the pool monitor with an engine."""
    monitor = get_pool_monitor()
    monitor.set_engine(engine)
    logger.info("Database pool monitor initialized")
    return monitor

def check_pool_health() -> Dict:
    """Quick health check for the connection pool."""
    monitor = get_pool_monitor()
    return monitor.get_pool_summary()

def log_pool_status():
    """Log current pool status."""
    monitor = get_pool_monitor()
    monitor.log_pool_status()

# Context manager for monitoring connection usage
class ConnectionMonitor:
    """Context manager to monitor individual connection usage."""
    
    def __init__(self, operation_name: str = "unknown"):
        self.operation_name = operation_name
        self.start_time = None
        self.monitor = get_pool_monitor()
        
    def __enter__(self):
        self.start_time = time.time()
        metrics = self.monitor.get_pool_metrics()
        if metrics:
            logger.debug(f"Connection acquired for {self.operation_name} "
                        f"(pool utilization: {metrics.utilization_percent:.1f}%)")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            logger.debug(f"Connection released after {duration:.2f}s for {self.operation_name}")
            
        # Log any exceptions
        if exc_type:
            logger.error(f"Exception in {self.operation_name}: {exc_val}")
            
        # Check pool health after operation
        metrics = self.monitor.get_pool_metrics()
        if metrics and metrics.is_critical():
            logger.warning(f"High pool utilization after {self.operation_name}: "
                         f"{metrics.utilization_percent:.1f}%") 