import unicodedata
import logging
import functools
import time
import random

def normalize_text(text: str) -> str:
    """Normalize and clean Unicode text for consistent ASCII representation."""
    if not text:
        return ""
    try:
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    except Exception as e:
        logging.warning(f"[normalize_text] Failed normalization: {e}")
        return text

def retry(exceptions, tries=3, delay=2, backoff=2):
    """
    Decorator that retries a function if specified exceptions occur.
    
    Parameters:
        exceptions (tuple): Exceptions to catch.
        tries (int): Number of attempts.
        delay (int): Initial wait time between retries.
        backoff (int): Backoff multiplier.

    Usage:
        @retry((requests.exceptions.RequestException,))
        def unreliable_function(): ...
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"[retry] {func.__name__} failed: {e}. Retrying in {_delay}s...")
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator_retry

def log_and_print(message: str, level: str = "info"):
    """Helper to log and print consistently across modules."""
    print(message)
    getattr(logging, level.lower(), logging.info)(message)