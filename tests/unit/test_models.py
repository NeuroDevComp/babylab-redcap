"""Test database models
"""

from datetime import datetime
import pytest
from babylab import models


def test_post_request(token):
    """Test ``post_request``."""
    assert models.post_request(
        fields={
            "content": "version",
        },
        token=token,
    ).ok


def test_redcap_version(token):
    """Test ``redcap_version``."""
    version = models.get_redcap_version(token=token)
    assert version
    assert isinstance(version, str)
    assert len(version.split(".")) == 3
    with pytest.raises(TypeError):
        models.get_redcap_version()
    with pytest.raises(TypeError):
        models.get_redcap_version(token)  # pylint: disable=too-many-function-args
    assert not models.get_redcap_version(token="wrongtoken")
    with pytest.raises(ValueError):
        models.get_redcap_version(token="bad#token")


def test_get_data_dict(token):
    """Test ``get_records``."""
    data_dict = models.get_data_dict(token=token)
    assert isinstance(data_dict, dict)
    assert all(isinstance(v, dict) for v in data_dict.values())
    with pytest.raises(TypeError):
        models.get_data_dict()


def test_get_records(token):
    """Test ``get_records``."""
    records = models.get_records(token=token)
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)
    with pytest.raises(TypeError):
        models.get_records()


def test_add_participant(participant_data, token):
    """Test ``add_participant``."""
    models.add_participant(participant_data, modifying=False, token=token)
    with pytest.raises(TypeError):
        models.add_participant(participant_data)


def test_redcap_backup(token) -> dict:
    """Test ``redcap_backup``."""
    models.redcap_backup(token=token)
    with pytest.raises(TypeError):
        models.redcap_backup()


def test_participant_class(participant_record):
    """Test participant class."""
    p = models.Participant(participant_record)
    assert hasattr(p, "record_id")
    assert hasattr(p, "data")

    assert isinstance(p.record_id, str)
    assert isinstance(p.data, dict)


def test_appointment_class(appointment_record):
    """Test appointment class."""
    a = models.Appointment(appointment_record)
    assert hasattr(a, "appointment_id")
    assert hasattr(a, "record_id")
    assert hasattr(a, "date")
    assert hasattr(a, "status")
    assert hasattr(a, "data")

    assert isinstance(a.appointment_id, str)
    assert isinstance(a.record_id, str)
    assert isinstance(a.date, datetime)
    assert isinstance(a.status, str)
    assert isinstance(a.data, dict)


def test_questionnaire_class(questionnaire_record):
    """Test questionnaire class."""
    q = models.Questionnaire(questionnaire_record)
    assert hasattr(q, "questionnaire_id")
    assert hasattr(q, "isestimated")
    assert hasattr(q, "record_id")
    assert hasattr(q, "data")
