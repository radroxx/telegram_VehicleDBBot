"""Cache lib"""

import logging
import time


logger = logging.getLogger("cache")


def cache_wipe_all():
    """Wipe all data in cache"""
    global GLOBAL_AWS_LAMBDA_CACHE # pylint: disable=W0601
    GLOBAL_AWS_LAMBDA_CACHE = {}


def cache_init():
    """Init cache"""
    try:
        if GLOBAL_AWS_LAMBDA_CACHE:
            logger.debug("Cache exists")
    except NameError:
        logger.info("Init new cache")
        cache_wipe_all()


def cache_validate():
    """Validate and delete expired data"""
    time_now = time.time()
    keys = list(GLOBAL_AWS_LAMBDA_CACHE.keys())
    for key in keys:
        if GLOBAL_AWS_LAMBDA_CACHE[key]['expired'] < time_now:
            del GLOBAL_AWS_LAMBDA_CACHE[key]


def cache_write(key: str, value: any, ttl: int = 600):
    """Set data to cache"""
    GLOBAL_AWS_LAMBDA_CACHE[key] = {
        'expired': time.time() + ttl,
        'value': value
    }


def cache_exists(key: str):
    """Check exists key in cache"""
    data = GLOBAL_AWS_LAMBDA_CACHE.get(key, None)
    if data is None:
        return False
    if data['expired'] < time.time():
        del GLOBAL_AWS_LAMBDA_CACHE[key]
        return False
    return True


def cache_wipe_key(key: str):
    """Delete key from cache"""
    if cache_exists(key):
        del GLOBAL_AWS_LAMBDA_CACHE[key]


def cache_read(key: str, default = None) -> any:
    """Get data from cache"""

    if cache_exists(key) is False:
        return default
    return GLOBAL_AWS_LAMBDA_CACHE.get(key, {}).get("value", default)


def cache_size() -> int:
    """Return cache size"""
    return len(GLOBAL_AWS_LAMBDA_CACHE)
