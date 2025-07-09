"""Rate limiting for API endpoints."""

from datetime import datetime, timezone
from typing import Dict, Tuple, Optional
import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, window_size: int = 60, max_requests: int = 100):
        self.window_size = window_size  # Window size in seconds
        self.max_requests = max_requests  # Maximum requests per window
        self.requests = defaultdict(list)  # {ip: [timestamp, ...]}
        self.last_cleanup = time.time()
    
    def cleanup_old_requests(self, current_time: float) -> None:
        """Remove requests outside the current window."""
        if current_time - self.last_cleanup < 60:  # Cleanup once per minute
            return
            
        cutoff = current_time - self.window_size
        for ip in list(self.requests.keys()):
            self.requests[ip] = [ts for ts in self.requests[ip] if ts > cutoff]
            if not self.requests[ip]:
                del self.requests[ip]
        
        self.last_cleanup = current_time
    
    def is_rate_limited(self, ip: str) -> Tuple[bool, Optional[int]]:
        """Check if the IP is rate limited."""
        current_time = time.time()
        self.cleanup_old_requests(current_time)
        
        # Add current request
        self.requests[ip].append(current_time)
        
        # Check if rate limited
        if len(self.requests[ip]) > self.max_requests:
            # Calculate retry-after in seconds
            oldest_request = self.requests[ip][0]
            retry_after = int(oldest_request + self.window_size - current_time)
            return True, max(0, retry_after)
        
        return False, None

class ErrorEndpointRateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        window_size: int = 60,
        max_requests: int = 50  # More strict for error endpoints
    ):
        super().__init__(app)
        self.rate_limiter = RateLimiter(window_size, max_requests)
    
    async def dispatch(self, request: Request, call_next):
        # Only rate limit error-related endpoints
        if not self._is_error_endpoint(request.url.path):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        is_limited, retry_after = self.rate_limiter.is_rate_limited(client_ip)
        if is_limited:
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Too many error reports",
                    "retry_after": retry_after
                }
            )
        
        return await call_next(request)
    
    def _is_error_endpoint(self, path: str) -> bool:
        """Check if the path is an error-related endpoint."""
        error_patterns = [
            "/api/v1/errors",
            "/api/v1/logs",
            "/health"
        ]
        return any(pattern in path for pattern in error_patterns)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the client's IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host 