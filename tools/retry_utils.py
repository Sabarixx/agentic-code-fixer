"""Retry utility functions for wrapping LLM API calls with exponential backoff."""

from __future__ import annotations

import time
import functools
from typing import Callable, TypeVar, Any

T = TypeVar("T")


def invoke_with_exponential_backoff(
    fn: Callable[..., T],
    *args: Any,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    **kwargs: Any,
) -> T:
    """
    Invoke function `fn` with exponential backoff on transient errors.
    Delays: 2s, 4s, 8s across max_retries attempts.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as err:
            last_exception = err
            if attempt == max_retries:
                print(f"[RetryExhausted] Attempt {attempt}/{max_retries} failed: {err}")
                raise err
            print(f"[RetryBackoff] Attempt {attempt}/{max_retries} failed: {err}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= backoff_factor

    if last_exception:
        raise last_exception
    raise RuntimeError("Retry loop exited unexpectedly")
