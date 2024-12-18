"""Test database models
"""

from datetime import datetime
from babylab import models


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
