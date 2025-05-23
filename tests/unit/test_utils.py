"""Test util functions
"""

from typing import Generator
from datetime import date, datetime
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


def test_is_in_data_dict(data_dict: dict):
    """Test is_in_datadict."""
    assert utils.is_in_data_dict(["Successful"], "appointment_status", data_dict) == [
        "Successful"
    ]
    assert utils.is_in_data_dict(
        ["Successful", "Confirmed"], "appointment_status", data_dict
    ) == ["Successful", "Confirmed"]
    assert utils.is_in_data_dict("Successful", "appointment_status", data_dict) == [
        "Successful"
    ]

    assert utils.is_in_data_dict(
        ["mop_newborns_1_nirs"], "appointment_study", data_dict
    ) == ["mop_newborns_1_nirs"]
    assert utils.is_in_data_dict(
        ["mop_newborns_1_nirs", "mop_infants_1_hpp"], "appointment_study", data_dict
    ) == ["mop_newborns_1_nirs", "mop_infants_1_hpp"]
    assert utils.is_in_data_dict(
        "mop_newborns_1_nirs", "appointment_study", data_dict
    ) == ["mop_newborns_1_nirs"]

    with pytest.raises(ValueError):
        utils.is_in_data_dict(["Badname"], "appointment_status", data_dict)
        utils.is_in_data_dict(
            ["Badname", "Successful"], "appointment_status", data_dict
        )
        utils.is_in_data_dict("Badname", "appointment_status", data_dict)


def test_get_year_weeks():
    """Test get_year_weeks."""
    assert isinstance(utils.get_year_weeks(2025), Generator)
    assert isinstance(next(utils.get_year_weeks(2025)), date)


def test_get_week_n():
    """Test get_week_n."""
    assert isinstance(utils.get_week_n(datetime.today()), int)


def test_get_weekly_apts(data_dict, records_fixture):
    """Test get_weekly_apts."""
    assert isinstance(
        utils.get_weekly_apts(data_dict=data_dict, records=records_fixture), int
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict, records=records_fixture, study="mop_newborns_1_nirs"
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict,
            records=records_fixture,
            study="mop_newborns_1_nirs",
            status="Successful",
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict,
            records=records_fixture,
            study=["mop_newborns_1_nirs", "mop_infants_1_hpp"],
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict,
            records=records_fixture,
            study=["mop_newborns_1_nirs", "mop_infants_1_hpp"],
            status=["Successful", "Confirmed"],
        ),
        int,
    )
