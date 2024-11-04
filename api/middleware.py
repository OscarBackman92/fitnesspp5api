# api/middleware.py

import time
from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.middleware.common import CommonMiddleware
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class CustomCommonMiddleware(CommonMiddleware):
    """Custom middleware adding security headers and performance monitoring"""
    
    def process_request(self, request: HttpRequest) -> None:
        """Add request timestamp for performance monitoring"""
        request.start_time = time.time()

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add security headers and log request duration"""
        response = super().process_response(request, response)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add performance monitoring
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Request-Duration'] = str(duration)
            
            # Log slow requests (more than 1 second)
            if duration > 1:
                logger.warning(
                    f'Slow request: {request.path} took {duration:.2f}s',
                    extra={
                        'path': request.path,
                        'method': request.method,
                        'duration': duration
                    }
                )
        
        return response

class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Check rate limit
        if not self.check_rate_limit(ip):
            from django.http import HttpResponseTooManyRequests
            return HttpResponseTooManyRequests("Rate limit exceeded")
            
        return self.get_response(request)

    def get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '')

    def check_rate_limit(self, ip: str) -> bool:
        """Check if request is within rate limit"""
        cache_key = f'rate_limit:{ip}'
        requests = cache.get(cache_key, 0)
        
        if requests >= 100:  # 100 requests per minute
            return False
            
        cache.set(cache_key, requests + 1, 60)  # 60 seconds expiry
        return True

class RequestLoggingMiddleware:
    """Middleware for logging requests"""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Log request
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'user': request.user.username if request.user.is_authenticated else 'anonymous'
            }
        )
        
        response = self.get_response(request)
        
        # Log response
        logger.info(
            f"Response: {response.status_code}",
            extra={
                'status_code': response.status_code,
                'path': request.path,
            }
        )
        
        return response