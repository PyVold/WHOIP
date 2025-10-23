"""
Redis caching service for IP geolocation lookups.
Significantly reduces external API calls and improves performance.
"""
import json
import logging
from typing import Optional, Dict
from functools import wraps

logger = logging.getLogger(__name__)

# Redis client - will be initialized in app.py
redis_client = None


def init_cache(redis_url: str):
    """
    Initialize Redis connection.

    Args:
        redis_url: Redis connection URL

    Returns:
        Redis client or None if connection fails
    """
    global redis_client

    if not redis_url or redis_url == 'memory://':
        logger.info("Redis caching disabled (using in-memory fallback)")
        return None

    try:
        import redis
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        logger.info(f"Redis cache initialized: {redis_url}")
        return redis_client
    except ImportError:
        logger.warning("redis package not installed. Install with: pip install redis")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None


def cache_get(key: str) -> Optional[str]:
    """
    Get value from cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None
    """
    if not redis_client:
        return None

    try:
        return redis_client.get(key)
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


def cache_set(key: str, value: str, ttl: int = 3600):
    """
    Set value in cache with TTL.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds (default: 1 hour)

    Returns:
        True if successful
    """
    if not redis_client:
        return False

    try:
        redis_client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


def cache_delete(key: str):
    """
    Delete value from cache.

    Args:
        key: Cache key

    Returns:
        True if successful
    """
    if not redis_client:
        return False

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False


def cache_ip_lookup(ttl: int = 3600):
    """
    Decorator to cache IP geolocation lookups.

    Args:
        ttl: Cache time to live in seconds (default: 1 hour)

    Usage:
        @cache_ip_lookup(ttl=3600)
        def get_country_code(ipaddr):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(ipaddr, *args, **kwargs):
            # Generate cache key
            cache_key = f"ip:country:{ipaddr}"

            # Try to get from cache
            cached = cache_get(cache_key)
            if cached:
                logger.debug(f"Cache hit for IP: {ipaddr}")
                return cached

            # Cache miss - call actual function
            logger.debug(f"Cache miss for IP: {ipaddr}")
            result = func(ipaddr, *args, **kwargs)

            # Cache the result
            if result and result != 'private':
                cache_set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def cache_country_data(ttl: int = 86400):
    """
    Decorator to cache country metadata lookups.

    Args:
        ttl: Cache time to live in seconds (default: 24 hours)

    Usage:
        @cache_country_data(ttl=86400)
        def country_data(country_code):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(country_code, *args, **kwargs):
            # Generate cache key
            cache_key = f"country:data:{country_code}"

            # Try to get from cache
            cached = cache_get(cache_key)
            if cached:
                try:
                    logger.debug(f"Cache hit for country: {country_code}")
                    return json.loads(cached)
                except json.JSONDecodeError:
                    pass

            # Cache miss - call actual function
            logger.debug(f"Cache miss for country: {country_code}")
            result = func(country_code, *args, **kwargs)

            # Cache the result
            if result:
                try:
                    cache_set(cache_key, json.dumps(result), ttl)
                except Exception as e:
                    logger.error(f"Failed to cache country data: {e}")

            return result

        return wrapper
    return decorator


def get_cache_stats() -> Dict:
    """
    Get cache statistics.

    Returns:
        Dictionary with cache stats
    """
    if not redis_client:
        return {
            'status': 'disabled',
            'keys': 0
        }

    try:
        info = redis_client.info()
        return {
            'status': 'connected',
            'keys': redis_client.dbsize(),
            'memory_used': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'uptime_seconds': info.get('uptime_in_seconds', 0)
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def clear_cache_pattern(pattern: str):
    """
    Clear all cache keys matching pattern.

    Args:
        pattern: Redis key pattern (e.g., 'ip:country:*')

    Returns:
        Number of keys deleted
    """
    if not redis_client:
        return 0

    try:
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Cleared {deleted} cache keys matching: {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Failed to clear cache pattern {pattern}: {e}")
        return 0
