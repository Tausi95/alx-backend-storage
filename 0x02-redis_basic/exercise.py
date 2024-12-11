#!/usr/bin/env python3
"""0. Writing strings to Redis"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


class Cache:
    def __init__(self):
        """Initialize the Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store a value in Redis with a randomly generated key.
        Args:
            data: The data to be stored (str, bytes, int, or float).
        Returns:
            str: The generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using a callable.
        Args:
            key: The Redis key.
            fn: Optional callable to apply to the retrieved data.
        Returns:
            The original data, optionally processed by the callable.
        """
        value = self._redis.get(key)
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Retrieve data as a string."""
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieve data as an integer."""
        return self.get(key, fn=int)


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    Args:
        method: The method to be decorated.
    Returns:
        Callable: The wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the input and output history of a method.
    Args:
        method: The method to be decorated.
    Returns:
        Callable: The wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, output)
        return output
    return wrapper


def replay(method: Callable):
    """
    Display the call history of a method.
    Args:
        method: The method to display the history for.
    """
    redis = method.__self__._redis
    method_name = method.__qualname__
    inputs = redis.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis.lrange(f"{method_name}:outputs", 0, -1)
    print(f"{method_name} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{method_name}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")

