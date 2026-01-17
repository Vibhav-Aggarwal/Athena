#!/usr/bin/env python3
"""
Simple in-memory cache for Athena API
Reduces Neo4j query load for frequently accessed data
"""

import time
from typing import Any, Optional

class SimpleCache:
    """
    Thread-safe in-memory cache with TTL support
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache = {}
        self._default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return None

        self._stats["hits"] += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl if ttl is not None else self._default_ttl

        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }

        self._stats["sets"] += 1

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key existed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._stats["evictions"] += len(self._cache)

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self._stats,
            "size": len(self._cache),
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired = [k for k, v in self._cache.items() if now > v["expires_at"]]

        for key in expired:
            del self._cache[key]

        self._stats["evictions"] += len(expired)
        return len(expired)
