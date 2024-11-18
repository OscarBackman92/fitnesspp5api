from functools import wraps
from django.core.cache import cache
from django.db import transaction
import logging
import time
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar('T')

def cached_property_with_ttl(ttl: int = 300):
    """
    Decorator for caching property with TTL
    Args:
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func: Callable) -> property:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            cache_key = f'{self.__class__.__name__}_{self.id}_{func.__name__}'
            result = cache.get(cache_key)
            
            if result is None:
                result = func(self, *args, **kwargs)
                cache.set(cache_key, result, ttl)
            
            return result
        return property(wrapper)
    return decorator

def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure and log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(
            f'{func.__name__} took {execution_time:.2f} seconds to execute',
            extra={
                'execution_time': execution_time,
                'function': func.__name__
            }
        )
        return result
    return wrapper

def bulk_cache_update(objects: list, serializer_class: Any) -> None:
    """
    Bulk update cache for multiple objects
    Args:
        objects: List of objects to cache
        serializer_class: Serializer class to use for serialization
    """
    with transaction.atomic():
        for obj in objects:
            cache_key = f'{obj.__class__.__name__}_{obj.id}'
            serializer = serializer_class(obj)
            cache.set(cache_key, serializer.data, timeout=60*15)

def clear_cache_pattern(pattern: str) -> None:
    """
    Clear all cache keys matching a pattern
    Args:
        pattern: Pattern to match cache keys
    """
    keys = cache.keys(pattern)
    if keys:
        cache.delete_many(keys)

def cache_response(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator to cache view responses
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            cache_key = (
                f"{key_prefix}:{request.path}:"
                f"{request.query_params}:{request.user.id}"
            )
            
            response = cache.get(cache_key)
            
            if response is None:
                response = func(self, request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator