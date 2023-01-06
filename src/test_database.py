"""Test database methods"""

from .database import get_vehicle_by_plate

def test_get_vehicle_by_plate():
    """Test read vehicle by plate"""

    tmp_var = get_vehicle_by_plate("test")

    assert not tmp_var
