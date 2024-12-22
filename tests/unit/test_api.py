"""Test API."""

import os
from datetime import datetime
import pytest
from babylab import api


def test_post_request(token):
    """Test ``post_request``."""
    assert api.post_request(
        fields={
            "content": "version",
        },
        token=token,
    ).ok


def test_redcap_version(token):
    """Test ``redcap_version``."""
    version = api.get_redcap_version(token=token)
    assert version
    assert isinstance(version, str)
    assert len(version.split(".")) == 3
    with pytest.raises(TypeError):
        api.get_redcap_version()
    with pytest.raises(TypeError):
        api.get_redcap_version(token)  # pylint: disable=too-many-function-args
    assert not api.get_redcap_version(token="wrongtoken")
    with pytest.raises(ValueError):
        api.get_redcap_version(token="bad#token")


def test_datetimes_to_str():
    """Test ``test_datetimes_to_str`` function."""
    data = {
        "date_now": datetime(2024, 10, 24, 8, 48, 34, 685496),
        "date_today": datetime(2024, 10, 24, 8, 48),
        "date_str": "2024-05-12 5:12",
    }
    result = api.datetimes_to_strings(data)
    assert result["date_now"] == "2024-10-24 08:48:34"
    assert result["date_today"] == "2024-10-24 08:48"
    assert result["date_str"] == data["date_str"]


def test_get_data_dict(token):
    """Test ``get_records``."""
    data_dict = api.get_data_dict(token=token)
    assert isinstance(data_dict, dict)
    assert all(isinstance(v, dict) for v in data_dict.values())
    with pytest.raises(TypeError):
        api.get_data_dict()


def test_get_records(token):
    """Test ``get_records``."""
    records = api.get_records(token=token)
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)
    with pytest.raises(TypeError):
        api.get_records()


def test_add_participant(participant_data, token):
    """Test ``add_participant``."""
    api.add_participant(participant_data, token=token)
    with pytest.raises(TypeError):
        api.add_participant(participant_data)


def test_add_appointment(appointment_record, token):
    """Test ``add_appointment`` ."""
    api.add_appointment(appointment_record, token=token)
    with pytest.raises(TypeError):
        api.add_appointment(appointment_record)


def test_add_appointment_modifying(appointment_record, token):
    """Test ``add_appointment`` with ``modifying=True``."""
    api.add_participant(appointment_record, token=token)
    with pytest.raises(TypeError):
        api.add_participant(appointment_record)


def test_add_questionnaire(questionnaire_record, token):
    """Test ``add_appointment``."""
    api.add_questionnaire(questionnaire_record, token=token)
    with pytest.raises(TypeError):
        api.add_questionnaire(questionnaire_record)


def test_redcap_backup(token, tmp_path) -> dict:
    """Test ``redcap_backup``."""
    tmp_dir = tmp_path / "tmp"
    file = api.redcap_backup(dirpath=tmp_dir, token=token)
    assert os.path.exists(file)
    with pytest.raises(TypeError):
        api.redcap_backup(dirpath=tmp_dir)
