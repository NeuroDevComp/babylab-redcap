"""Test util functions
"""

import pytest
from babylab.src import utils


def test_fmt_percentage():
    """Test fmt_percentage."""
    with pytest.raises(ValueError):
        utils.fmt_percentage(-0.1)
    with pytest.raises(ValueError):
        utils.fmt_percentage(111)
    assert utils.fmt_percentage(0) == ""
    assert utils.fmt_percentage(1) == "1"
    assert utils.fmt_percentage(0.2) == "0"
    assert utils.fmt_percentage(55) == "55"
    assert utils.fmt_percentage(100) == "100"


def test_fmt_taxi_isbooked():
    """Test fmt_taxi_isbooked."""
    with pytest.raises(ValueError):
        utils.fmt_taxi_isbooked("Some address", "a")
    assert (
        utils.fmt_taxi_isbooked("Some address", "1")
        == "<p style='color: green;'>Yes</p>"
    )
    assert (
        utils.fmt_taxi_isbooked("Some address", "0") == "<p style='color: red;'>No</p>"
    )
    assert utils.fmt_taxi_isbooked("", "0") == ""
