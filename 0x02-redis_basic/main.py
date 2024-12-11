#!/usr/bin/env python3
"""
Main file
"""
import redis

Cache = __import__('exercise').Cache

cache1 = Cache()

data = b"hello"
key = cache1.store(data)
print(key)

local_redis = redis.Redis()
print(local_redis.get(key))


cache2 = Cache()

TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache2.store(value)
    assert cache2.get(key, fn=fn) == value

cache3 = Cache()

cache3.store(b"first")
print(cache3.get(cache3.store.__qualname__))

cache3.store(b"second")
cache3.store(b"third")
print(cache3.get(cache3.store.__qualname__))

cache4 = Cache()

s1 = cache4.store("first")
print(s1)
s2 = cache4.store("secont")
print(s2)
s3 = cache4.store("third")
print(s3)

inputs = cache4._redis.lrange("{}:inputs".format(cache4.store.__qualname__), 0, -1)
outputs = cache4._redis.lrange("{}:outputs".format(cache4.store.__qualname__), 0, -1)

print("inputs: {}".format(inputs))
print("outputs: {}".format(outputs))


replay = __import__("exercise").replay
cache5 = Cache()
cache5.store("foo")
cache5.store("bar")
cache5.store(42)
replay(cache5.store)
