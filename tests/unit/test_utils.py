"""Test util functions
"""

import pytest
from babylab import utils


def test_format_percentage():
    """Test format_percentage."""
    with pytest.raises(ValueError):
        utils.format_percentage(-0.1)
    with pytest.raises(ValueError):
        utils.format_percentage(1.1)
    assert utils.format_percentage(0) == ""
    assert utils.format_percentage(1) == "100"
    assert utils.format_percentage(0.2) == "20"
    assert utils.format_percentage(0.55) == "55"


def test_format_taxi_isbooked():
    """Test format_taxi_isbooked."""
    with pytest.raises(ValueError):
        utils.format_taxi_isbooked("Some address", "a")
    assert (
        utils.format_taxi_isbooked("Some address", "1")
        == "<p style='color: green;'>Yes</p>"
    )
    assert (
        utils.format_taxi_isbooked("Some address", "0")
        == "<p style='color: red;'>No</p>"
    )
    assert utils.format_taxi_isbooked("", "0") == ""
