"""
Tool call dispatcher and error handler with circuit breaker.
"""
import asyncio
import time
import functools
import httpx
from typing import Any, Callable, TypeVar, Coroutine, cast
from enum import Enum

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open and a call is attempted."""
    pass

class CircuitBreaker:
    """Circuit breaker implementation for tool calls."""
    
    def __init__(self, max_failures: int = 3, reset_timeout: int = 60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0.0
        self._lock = asyncio.Lock()

    async def _on_failure(self) -> None:
        async with self._lock:
            self.failures += 1
            if self.failures >= self.max_failures:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()
            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()

    async def _on_success(self) -> None:
        async with self._lock:
            self.failures = 0
            self.state = CircuitState.CLOSED

    async def call(self, func: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any) -> T:
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.reset_timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is currently OPEN.")

        try:
            # 5.0 second timeout for the function execution
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=5.0)
            await self._on_success()
            return result
        except asyncio.TimeoutError:
            await self._on_failure()
            raise Exception("Tool execution timed out after 5.0 seconds.")
        except httpx.TimeoutException as e:
            await self._on_failure()
            raise Exception(f"HTTP timeout occurred: {str(e)}")
        except Exception:
            await self._on_failure()
            raise

def tool_handler(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Decorator that wraps tool functions with timeout, error handling, and a circuit breaker.
    """
    breaker = CircuitBreaker()
    
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        return await breaker.call(func, *args, **kwargs)
        
    return wrapper
