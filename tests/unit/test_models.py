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


def test_records_class(records):
    """Test participant class."""
    assert hasattr(records, "appointments")
    assert hasattr(records, "participants")
    assert hasattr(records, "questionnaires")
    assert isinstance(records.appointments, models.RecordList)
    assert isinstance(records.participants, models.RecordList)
    assert isinstance(records.questionnaires, models.RecordList)


def test_records_class_participants(records):
    """Test records class (Participants)"""
    assert hasattr(records.participants, "records")
    assert hasattr(records.participants, "to_df")
    assert isinstance(records.participants.records, dict)
    assert all(
        isinstance(r, models.Participant) for r in records.participants.records.values()
    )


def test_records_class_appointments(records):
    """Test records class (Appointments)"""
    assert hasattr(records.appointments, "records")
    assert hasattr(records.appointments, "to_df")
    assert isinstance(records.appointments.records, dict)
    assert all(
        isinstance(r, models.Appointment) for r in records.appointments.records.values()
    )


def test_records_class_questionnaires(records):
    """Test records class (Questionnaires)"""
    assert hasattr(records.questionnaires, "records")
    assert hasattr(records.questionnaires, "to_df")
    assert isinstance(records.questionnaires.records, dict)
    assert all(
        isinstance(r, models.Questionnaire)
        for r in records.questionnaires.records.values()
    )
