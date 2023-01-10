"""Tests cache module"""

from .cache import (
    cache_init,
    cache_wipe_all,
    cache_write,
    cache_read,
    cache_size,
    cache_validate,
    cache_exists,
    cache_wipe_key
    )


def test_cache_init():
    """Test init cache"""

    cache_init()


def test_cache_write():
    """Test write data to cache"""

    cache_write("unittest_write", 1)

    assert cache_read("unittest_write") == 1


def test_cache_read():
    """Test read data from cache"""

    cache_write("unittest_write", 2)

    assert cache_read("unittest_write") == 2
    assert cache_read("unittest_write_2") is None
    assert cache_read("unittest_write_2", 1) == 1


def test_cache_wipe_all():
    """Test wipe all data in cache"""

    cache_write("unittest_write", 3)
    assert cache_read("unittest_write") == 3
    cache_wipe_all()
    assert cache_read("unittest_write") is None


def test_cache_validate():
    """Test validate cache and delete expired data"""

    cache_write("unittest_write", 4, ttl = -1)
    assert cache_size() == 1
    cache_validate()
    assert cache_size() == 0


def test_cache_exists():
    """Test exists key in cache"""

    cache_write("unittest_write", 5, ttl = -1)
    assert cache_exists("unittest_write") is False
    cache_write("unittest_write", 5, ttl = 1)
    assert cache_exists("unittest_write") is True


def test_cache_wipe_key():
    """Test wipe key in cache"""

    cache_write("unittest_write", 5, ttl = 1)
    assert cache_exists("unittest_write") is True
    cache_wipe_key("unittest_write")
    assert cache_exists("unittest_write") is False


def test_cache_double_init():
    """Test wipe key in cache"""

    cache_write("unittest_write", 6, ttl = 1)
    assert cache_read("unittest_write") == 6
    cache_init()
    assert cache_read("unittest_write") == 6
