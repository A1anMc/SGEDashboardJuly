"""
Robust API Client with Retry Logic and Connection Monitoring
Handles all external API calls with reliability and monitoring
"""

import asyncio
import aiohttp
import requests
import time
import logging
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager
from urllib.parse import urljoin, urlparse
from app.core.config import settings
import json

logger = logging.getLogger(__name__)

class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retryable_status_codes: List[int] = field(default_factory=lambda: [500, 502, 503, 504, 429])
    retryable_exceptions: List[type] = field(default_factory=lambda: [
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        aiohttp.ClientError,
        asyncio.TimeoutError
    ])

@dataclass
class APIResponse:
    """Standardized API response wrapper."""
    status_code: int
    data: Optional[Dict] = None
    text: Optional[str] = None
    headers: Optional[Dict] = None
    url: Optional[str] = None
    elapsed: Optional[float] = None
    attempt: int = 1
    success: bool = False
    error: Optional[str] = None

@dataclass
class ConnectionMetrics:
    """Metrics for API connection monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_retries: int = 0
    avg_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    endpoints: Dict[str, Dict] = field(default_factory=dict)

class APIClient:
    """Robust API client with retry logic and monitoring."""
    
    def __init__(self, 
                 base_url: str = "",
                 timeout: float = 30.0,
                 retry_config: Optional[RetryConfig] = None,
                 headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self.default_headers = self._get_default_headers()
        if headers:
            self.default_headers.update(headers)
        
        self.metrics = ConnectionMetrics()
        self.session = None
        self._circuit_breaker_until: Optional[datetime] = None
        self._circuit_breaker_failures = 0
        
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        return {
            "User-Agent": f"NavImpact/{settings.VERSION}",
            "Accept": "application/json, text/html, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self._circuit_breaker_until is None:
            return False
        
        if datetime.now() > self._circuit_breaker_until:
            # Reset circuit breaker
            self._circuit_breaker_until = None
            self._circuit_breaker_failures = 0
            logger.info("Circuit breaker reset")
            return False
        
        return True
    
    def _update_circuit_breaker(self, success: bool):
        """Update circuit breaker state."""
        if success:
            self._circuit_breaker_failures = 0
            self._circuit_breaker_until = None
        else:
            self._circuit_breaker_failures += 1
            
            # Open circuit breaker after 5 consecutive failures
            if self._circuit_breaker_failures >= 5:
                self._circuit_breaker_until = datetime.now() + timedelta(minutes=5)
                logger.warning("Circuit breaker opened due to consecutive failures")
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry with exponential backoff."""
        delay = self.retry_config.initial_delay * (self.retry_config.backoff_factor ** (attempt - 1))
        delay = min(delay, self.retry_config.max_delay)
        
        if self.retry_config.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    def _should_retry(self, response: APIResponse, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.retry_config.max_retries:
            return False
        
        if response.status_code in self.retry_config.retryable_status_codes:
            return True
        
        if response.error and any(
            isinstance(response.error, exc) 
            for exc in self.retry_config.retryable_exceptions
        ):
            return True
        
        return False
    
    def _update_metrics(self, response: APIResponse, endpoint: str):
        """Update connection metrics."""
        self.metrics.total_requests += 1
        
        if response.success:
            self.metrics.successful_requests += 1
            self.metrics.last_success = datetime.now()
            self.metrics.consecutive_failures = 0
        else:
            self.metrics.failed_requests += 1
            self.metrics.last_failure = datetime.now()
            self.metrics.consecutive_failures += 1
        
        self.metrics.total_retries += (response.attempt - 1)
        
        # Update response time average
        if response.elapsed:
            total_time = self.metrics.avg_response_time * (self.metrics.total_requests - 1)
            self.metrics.avg_response_time = (total_time + response.elapsed) / self.metrics.total_requests
        
        # Update endpoint-specific metrics
        if endpoint not in self.metrics.endpoints:
            self.metrics.endpoints[endpoint] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "avg_response_time": 0.0,
                "last_accessed": None
            }
        
        endpoint_metrics = self.metrics.endpoints[endpoint]
        endpoint_metrics["requests"] += 1
        endpoint_metrics["last_accessed"] = datetime.now()
        
        if response.success:
            endpoint_metrics["successes"] += 1
        else:
            endpoint_metrics["failures"] += 1
        
        if response.elapsed:
            total_endpoint_time = endpoint_metrics["avg_response_time"] * (endpoint_metrics["requests"] - 1)
            endpoint_metrics["avg_response_time"] = (total_endpoint_time + response.elapsed) / endpoint_metrics["requests"]
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        
        if self.base_url:
            return urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        return endpoint
    
    def request(self, 
                method: Union[RequestMethod, str],
                endpoint: str,
                data: Optional[Dict] = None,
                params: Optional[Dict] = None,
                headers: Optional[Dict] = None,
                timeout: Optional[float] = None,
                **kwargs) -> APIResponse:
        """Make a synchronous HTTP request with retry logic."""
        
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            return APIResponse(
                status_code=503,
                error="Circuit breaker is open",
                url=self._build_url(endpoint),
                success=False
            )
        
        if isinstance(method, RequestMethod):
            method = method.value
        
        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout
        
        # Prepare headers
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Validate external URL
        if not self._is_allowed_domain(url):
            return APIResponse(
                status_code=403,
                error=f"Domain not allowed: {urlparse(url).netloc}",
                url=url,
                success=False
            )
        
        attempt = 1
        while attempt <= self.retry_config.max_retries:
            try:
                start_time = time.time()
                
                # Make request
                response = requests.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    params=params,
                    headers=request_headers,
                    timeout=request_timeout,
                    **kwargs
                )
                
                elapsed = time.time() - start_time
                
                # Parse response
                response_data = None
                try:
                    response_data = response.json()
                except:
                    pass
                
                api_response = APIResponse(
                    status_code=response.status_code,
                    data=response_data,
                    text=response.text,
                    headers=dict(response.headers),
                    url=url,
                    elapsed=elapsed,
                    attempt=attempt,
                    success=response.status_code < 400
                )
                
                # Update metrics and circuit breaker
                self._update_metrics(api_response, endpoint)
                self._update_circuit_breaker(api_response.success)
                
                # Return if successful or not retryable
                if api_response.success or not self._should_retry(api_response, attempt):
                    return api_response
                
                logger.warning(f"Request failed (attempt {attempt}): {response.status_code} - {url}")
                
            except Exception as e:
                elapsed = time.time() - start_time
                
                api_response = APIResponse(
                    status_code=0,
                    error=str(e),
                    url=url,
                    elapsed=elapsed,
                    attempt=attempt,
                    success=False
                )
                
                # Update metrics and circuit breaker
                self._update_metrics(api_response, endpoint)
                self._update_circuit_breaker(False)
                
                logger.error(f"Request exception (attempt {attempt}): {str(e)} - {url}")
                
                if not self._should_retry(api_response, attempt):
                    return api_response
            
            # Wait before retry
            if attempt < self.retry_config.max_retries:
                delay = self._calculate_delay(attempt)
                logger.info(f"Retrying in {delay:.2f}s... (attempt {attempt + 1})")
                time.sleep(delay)
            
            attempt += 1
        
        return api_response
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> APIResponse:
        """Make a GET request."""
        return self.request(RequestMethod.GET, endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> APIResponse:
        """Make a POST request."""
        return self.request(RequestMethod.POST, endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> APIResponse:
        """Make a PUT request."""
        return self.request(RequestMethod.PUT, endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        """Make a DELETE request."""
        return self.request(RequestMethod.DELETE, endpoint, **kwargs)
    
    def _is_allowed_domain(self, url: str) -> bool:
        """Check if the domain is allowed for external requests."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Check against allowed domains
            allowed_domains = [d.lower() for d in settings.ALLOWED_EXTERNAL_DOMAINS]
            
            # Exact match
            if domain in allowed_domains:
                return True
            
            # Check for subdomain matches
            for allowed_domain in allowed_domains:
                if domain.endswith(f".{allowed_domain}"):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking domain: {e}")
            return False
    
    def get_metrics(self) -> Dict:
        """Get connection metrics."""
        success_rate = 0.0
        if self.metrics.total_requests > 0:
            success_rate = (self.metrics.successful_requests / self.metrics.total_requests) * 100
        
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": round(success_rate, 2),
            "total_retries": self.metrics.total_retries,
            "avg_response_time": round(self.metrics.avg_response_time, 3),
            "last_success": self.metrics.last_success.isoformat() if self.metrics.last_success else None,
            "last_failure": self.metrics.last_failure.isoformat() if self.metrics.last_failure else None,
            "consecutive_failures": self.metrics.consecutive_failures,
            "circuit_breaker_open": self._is_circuit_breaker_open(),
            "endpoints": self.metrics.endpoints
        }
    
    def reset_metrics(self):
        """Reset connection metrics."""
        self.metrics = ConnectionMetrics()
        self._circuit_breaker_until = None
        self._circuit_breaker_failures = 0
    
    def health_check(self) -> Dict:
        """Perform a health check."""
        if self.base_url:
            # Try to make a simple request to base URL
            response = self.get("")
            return {
                "status": "healthy" if response.success else "unhealthy",
                "base_url": self.base_url,
                "response_time": response.elapsed,
                "status_code": response.status_code,
                "circuit_breaker_open": self._is_circuit_breaker_open()
            }
        else:
            return {
                "status": "healthy",
                "base_url": None,
                "circuit_breaker_open": self._is_circuit_breaker_open()
            }

# Global API client instances for different services
_api_clients: Dict[str, APIClient] = {}

def get_api_client(service_name: str, base_url: str = "", **kwargs) -> APIClient:
    """Get or create an API client for a specific service."""
    if service_name not in _api_clients:
        _api_clients[service_name] = APIClient(base_url=base_url, **kwargs)
    return _api_clients[service_name]

def get_scraper_client(source: str) -> APIClient:
    """Get an API client configured for a specific scraper source."""
    if source not in settings.ALLOWED_SCRAPER_SOURCES:
        raise ValueError(f"Unknown scraper source: {source}")
    
    source_config = settings.ALLOWED_SCRAPER_SOURCES[source]
    base_url = source_config.get("base_url", "")
    
    # Configure retry for scrapers (more aggressive)
    retry_config = RetryConfig(
        max_retries=5,
        initial_delay=2.0,
        max_delay=120.0,
        backoff_factor=2.0,
        jitter=True
    )
    
    return get_api_client(
        service_name=f"scraper_{source}",
        base_url=base_url,
        retry_config=retry_config,
        timeout=60.0
    )

def get_all_client_metrics() -> Dict[str, Dict]:
    """Get metrics for all API clients."""
    return {
        service_name: client.get_metrics()
        for service_name, client in _api_clients.items()
    }

def reset_all_client_metrics():
    """Reset metrics for all API clients."""
    for client in _api_clients.values():
        client.reset_metrics()

def health_check_all_clients() -> Dict[str, Dict]:
    """Perform health checks for all API clients."""
    return {
        service_name: client.health_check()
        for service_name, client in _api_clients.items()
    } 