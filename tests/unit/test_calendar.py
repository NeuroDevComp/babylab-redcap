"""Test calendar"""

import pytest
from babylab import calendar as cal
from datetime import datetime


def test_get_age():
    """Test ``get_age``"""
    assert isinstance(cal.get_age("2024-05-01"), list)
    assert all(isinstance(d, int) for d in cal.get_age("2024-05-01"))
    assert len(cal.get_age("2024-05-01")) == 2
    assert isinstance(cal.get_age("2024-05-01"), list)

    assert isinstance(cal.get_age("2024-05-01", "2024-12-17"), list)
    assert all(isinstance(d, int) for d in cal.get_age("2024-05-01", "2024-12-17"))
    assert len(cal.get_age("2024-05-01", "2024-12-17")) == 2
    assert isinstance(cal.get_age("2024-05-01", "2024-12-17"), list)
    assert all(d < 0 for d in cal.get_age("2025-05-01", "2024-12-17"))
    with pytest.raises(ValueError):
        cal.get_age("a2025-05-01")
        cal.get_age("01-05-2024")
        cal.get_age("a2025-05-01", "2024-12-17")
        cal.get_age("01-05-2024", "2024-12-17")
        cal.get_age("2024/05/01", "2024-12-17")


def test_get_birth_date():
    """Test ``get_birth_date``."""

    assert isinstance(
        cal.get_birth_date("2:1"), datetime
    )  # pylint: disable=undefined-variable
    assert cal.get_birth_date("0:1", "2024-12-17") == datetime(2024, 12, 16, 0, 0)
    assert cal.get_birth_date("1:0", "2024-12-17") == datetime(2024, 11, 17, 0, 0)
