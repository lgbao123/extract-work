"""
Decorators Module

Common decorators for functions
"""

import time
import functools
from typing import Callable, Any
from .logger import get_logger
from .exceptions import RateLimitError

logger = get_logger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
        
    Examples:
        @retry(max_attempts=3, delay=2.0)
        def fetch_data():
            # Some operation that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def timing(func: Callable) -> Callable:
    """
    Timing decorator to measure function execution time
    
    Examples:
        @timing
        def process_data():
            # Some operation
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        elapsed = end_time - start_time
        logger.debug(f"{func.__name__} took {elapsed:.3f}s to execute")
        
        return result
    
    return wrapper


def rate_limit(calls_per_period: int = 50, period: float = 60.0):
    """
    Rate limiting decorator with automatic waiting
    
    Args:
        calls_per_period: Maximum number of calls allowed
        period: Time period in seconds
        
    Examples:
        @rate_limit(calls_per_period=10, period=60)
        def api_call():
            # API call that should be rate limited
            pass
    """
    def decorator(func: Callable) -> Callable:
        calls = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal calls
            
            now = time.time()
            
            # Remove old calls outside the period
            calls = [call_time for call_time in calls if now - call_time < period]
            
            # Check if limit exceeded - wait if necessary
            if len(calls) >= calls_per_period:
                wait_time = period - (now - calls[0]) + 1.0  # Add 1 second buffer
                logger.warning(
                    f"Rate limit approaching for {func.__name__}. Waiting {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
                # Clean up old calls after waiting
                now = time.time()
                calls = [call_time for call_time in calls if now - call_time < period]
            
            # Add current call
            calls.append(now)
            
            # Add small delay between calls to avoid bursts
            time.sleep(0.5)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_errors(logger_instance=None):
    """
    Decorator to log errors from functions
    
    Args:
        logger_instance: Logger to use (optional)
        
    Examples:
        @log_errors()
        def risky_operation():
            # Some operation that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger_instance
        if logger_instance is None:
            logger_instance = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger_instance.error(
                    f"Error in {func.__name__}: {type(e).__name__}: {e}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def cache_result(maxsize: int = 128):
    """
    Simple caching decorator (wrapper around functools.lru_cache)
    
    Args:
        maxsize: Maximum cache size
        
    Examples:
        @cache_result(maxsize=100)
        def expensive_calculation(x):
            return x ** 2
    """
    def decorator(func: Callable) -> Callable:
        return functools.lru_cache(maxsize=maxsize)(func)
    return decorator
