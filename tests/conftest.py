"""
Fixtures for testing
"""

import os
from string import digits, ascii_lowercase
from random import choice, choices
from datetime import datetime
import pytest
from dotenv import load_dotenv
from babylab import models
from babylab import create_app


@pytest.fixture
def token():
    """API test token.

    Returns:
        str: API test token.
    """
    return get_api_key()


def generate_str(n: str = 7) -> str:
    """Generate random string of ASCII characters.

    Args:
        nchar (str, optional): Number of characters in the string. Defaults to 7.

    Returns:
        str: Random string of characters of length ``n``.
    """
    return "".join(choices(ascii_lowercase + digits, k=n))


def generate_phone() -> str:
    """Generate random phone number (no prefix).

    Returns:
        str: Random phone number.
    """
    return "".join([str(x) for x in choices(range(9), k=9)])


def generate_email() -> str:
    """Generate random e-mail address.

    Returns:
        str: Random e-mail address.
    """
    return generate_str() + "@" + generate_str() + ".com"


def participant_data_dict() -> dict:
    """Generate random participant data dictionary.

    Returns:
        dict: Random participant data dictionary.
    """
    date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")

    data = {
        "record_id": "0",
        "participant_date_created": date_now,
        "participant_date_updated": date_now,
        "participant_name": generate_str(),
        "participant_age_now_months": str(choice(range(12))),
        "participant_age_now_days": str(choice(range(31))),
        "participant_sex": str(choice(range(1, 6))),
        "participant_twin": "",
        "participant_parent1_name": generate_str(),
        "participant_parent1_surname": generate_str(),
        "participant_parent2_name": generate_str(),
        "participant_parent2_surname": generate_str(),
        "participant_email1": generate_email(),
        "participant_phone1": generate_phone(),
        "participant_email2": generate_email(),
        "participant_phone2": generate_phone(),
        "participant_address": generate_str(),
        "participant_city": generate_str(),
        "participant_postcode": "".join([str(x) for x in choices(range(9), k=5)]),
        "participant_birth_type": choice(["1", "2"]),
        "participant_gest_weeks": str(choice(range(34, 43))),
        "participant_birth_weight": str(choice(range(2700, 4500))),
        "participant_head_circumference": str(choice(range(32, 38))),
        "participant_apgar1": str(choice(range(10))),
        "participant_apgar2": str(choice(range(10))),
        "participant_apgar3": str(choice(range(10))),
        "participant_hearing": choice(["1", "2"]),
        "participant_diagnoses": generate_str(50),
        "participant_comments": " ".join([generate_str(25) for _ in range(3)]),
        "participants_complete": "2",
    }

    return data


@pytest.fixture
def participant_data() -> dict:
    """Participant data.

    Returns:
        dict: Participant data.
    """
    return participant_data_dict()


def create_record(option: str) -> dict:
    """Create a REDCap record.

    Returns:
        dict: A REDCap record.
    """
    if option not in ["participant", "appointment", "questionnaire"]:
        raise ValueError(
            "option must be one of 'participant', 'appointment', or 'questionnaire'"
        )
    if option == "participant":
        return {
            "record_id": "0",
            "participant_date_created": datetime.strptime(
                "2024-12-16 11:13:00", "%Y-%m-%d %H:%M:%S"
            ),
            "participant_date_updated": datetime.strptime(
                "2024-12-16 11:13:00", "%Y-%m-%d %H:%M:%S"
            ),
            "participant_name": generate_str(),
            "participant_age_now_months": choice(range(12)),
            "participant_age_now_days": choice(range(31)),
            "participant_days_since_last_appointment": "",
            "participant_sex": str(choice(range(1, 6))),
            "participant_twin": "",
            "participant_parent1_name": generate_str(),
            "participant_parent1_surname": generate_str(),
            "participant_email1": generate_email(),
            "participant_phone1": generate_phone(),
            "participant_parent2_name": generate_str(),
            "participant_parent2_surname": generate_str(),
            "participant_email2": generate_email(),
            "participant_phone2": generate_str(),
            "participant_address": generate_str(),
            "participant_city": generate_str(),
            "participant_postcode": "".join([str(x) for x in choices(range(9), k=5)]),
            "participant_birth_type": choice(["1", "2"]),
            "participant_gest_weeks": str(choice(range(34, 43))),
            "participant_birth_weight": str(choice(range(2700, 4500))),
            "participant_head_circumference": str(choice(range(32, 38))),
            "participant_apgar1": str(choice(range(10))),
            "participant_apgar2": str(choice(range(10))),
            "participant_apgar3": str(choice(range(10))),
            "participant_hearing": choice(["1", "2"]),
            "participant_diagnoses": generate_str(50),
            "participant_comments": " ".join([generate_str(25) for _ in range(3)]),
            "participants_complete": "2",
        }

    if option == "appointment":
        return {
            "record_id": "1",
            "redcap_repeat_instrument": "appointments",
            "redcap_repeat_instance": 1,
            "appointment_study": "2",
            "appointment_date_created": datetime.strptime(
                "2024-12-12 14:09:00", "%Y-%m-%d %H:%M:%S"
            ),
            "appointment_date_updated": datetime.strptime(
                "2024-12-14 12:08:00", "%Y-%m-%d %H:%M:%S"
            ),
            "appointment_date": datetime.strptime("2024-12-31 14:09", "%Y-%m-%d %H:%M"),
            "appointment_taxi_address": generate_str(),
            "appointment_taxi_isbooked": choice(["0", "1"]),
            "appointment_status": str(choice(range(1, 6))),
            "appointment_comments": ". ".join([generate_str(25) for _ in range(3)]),
            "appointments_complete": "2",
        }

    return {
        "record_id": "1",
        "redcap_repeat_instrument": "language",
        "redcap_repeat_instance": 1,
        "language_date_created": datetime.strptime(
            "2024-12-12 14:24:00", "%Y-%m-%d %H:%M:%S"
        ),
        "language_date_updated": datetime.strptime(
            "2024-12-12 14:24:00", "%Y-%m-%d %H:%M:%S"
        ),
        "language_isestimated": "1",
        "language_lang1": "17",
        "language_lang1_exp": "80",
        "language_lang2": "13",
        "language_lang2_exp": "10",
        "language_lang3": "16",
        "language_lang3_exp": "10",
        "language_lang4": "0",
        "language_lang4_exp": "0",
        "language_comments": "",
        "language_complete": "2",
    }


@pytest.fixture
def participant_record() -> dict:
    """Create REDcap record fixture.

    Returns:
        dict: A REDcap record fixture.
    """
    return create_record("participant")


@pytest.fixture
def appointment_record() -> dict:
    """Create REDcap record fixture.

    Returns:
        dict: A REDcap record fixture.
    """
    return create_record("appointment")


@pytest.fixture
def questionnaire_record() -> dict:
    """Create REDcap record fixture.

    Returns:
        dict: A REDCap record fixture.
    """
    return create_record("questionnaire")


@pytest.fixture
def records() -> list:
    """Create REDCap participant record list fixture.

    Returns:
        list: A REDCap record list fixture.
    """
    return models.Records(token=get_api_key())


@pytest.fixture
def app():
    """App factory for testing."""
    return create_app()
