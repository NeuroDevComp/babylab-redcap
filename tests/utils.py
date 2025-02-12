"""Utils for testing suite."""

import datetime
from string import digits, ascii_lowercase
from random import choice, choices
import win32com as win
from babylab.src import api
from babylab.app import config as conf


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


def check_email_received(account: str = "gonzalo.garcia@sjd.es"):
    """Check that an email has been received."""
    # create an instance of the Outlook application
    outlook = win.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    # iterate through all accounts to find the specified one
    for acc in outlook.Folders:
        if acc.Name == account:
            inbox = acc.Folders["Inbox"]
            messages = inbox.Items
            # sort messages by received time in descending order
            messages.Sort("[ReceivedTime]", True)
            latest_message = messages.GetFirst()
            if latest_message:
                return {
                    "sender": latest_message.SenderName,
                    "subject": latest_message.Subject,
                    "timestamp": latest_message.ReceivedTime,
                }
            return False
    return False


def check_event_created(ppt_id: str, account: str = "gonzalo.garcia@sjd.es"):
    """Check that an email has been received."""
    # create an instance of the Outlook application
    outlook = win.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    recipient = outlook.createRecipient(account)
    shared_cal = outlook.GetSharedDefaultFolder(recipient, 9).Folders(
        "Appointments - Test"
    )
    for apt in shared_cal.Items:
        if ppt_id in apt.Subject:
            return {
                "subject": apt.Subject,
            }
    return False


def generate_lang_exp():
    """Create vector of language exposures.

    Returns:
        list[float]: Vector of language exposures that adds up to 100.
    """
    nlangs = choice(range(1, 4))
    exp = [0] * 4
    for l in range(1, nlangs):
        exp[l] = choice(range(100 - sum(exp)))
    exp[-1] = 100 - sum(exp[:-1])
    exp.sort(reverse=True)
    return exp


def get_data_dict() -> dict:
    """Create REDcap record fixture.

    Returns:
        dict: A REDcap record fixture.
    """
    return api.get_data_dict(token=conf.get_api_key())


def create_finput_ppt(is_new: bool = True) -> dict:
    """Simulate form input to test POST request in participants.

    Args:
        is_new (bool, optional): Should a new record be created? Defaults to True.

    Returns:
        dict: Simulated form input.
    """
    recs = api.Records(token=conf.get_api_key())
    ppt_id = choice(list(recs.participants.records.keys()))
    data = {
        "record_id": "new" if is_new else ppt_id,
        "inputName": generate_str(),
        "inputParent1Name": generate_str(),
        "inputSource": choice(range(1, 3)),
        "inputSex": choice(range(1, 6)),
        "inputParent1Surname": generate_str(),
        "inputParent2Name": generate_str(),
        "inputParent2Surname": generate_str(),
        "inputAgeMonths": choice(range(12)),
        "inputAgeDays": choice(range(31)),
        "inputNormalHearing": choice(["1", "2"]),
        "inputTwinID": "",
        "inputComments": " ".join([generate_str(25) for _ in range(3)]),
        "inputEmail1": generate_email(),
        "inputPhone1": generate_phone(),
        "inputEmail2": generate_email(),
        "inputPhone2": generate_phone(),
        "inputAddress": generate_str(),
        "inputCity": generate_str(),
        "inputPostcode": "".join([str(x) for x in choices(range(9), k=5)]),
        "inputBirthWeight": choice(range(2700, 4500)),
        "inputDeliveryType": choice(["1", "2"]),
        "inputGestationalWeeks": choice(range(34, 43)),
        "inputHeadCircumference": choice(range(32, 38)),
        "inputApgar1": choice(range(10)),
        "inputApgar2": choice(range(10)),
        "inputApgar3": choice(range(10)),
        "inputDiagnoses": generate_str(50),
    }
    data = {k: str(v) for k, v in data.items()}
    return data


def create_finput_apt(is_new: bool = True) -> dict:
    """Simulate form input to test POST request in appointments.

    Args:
        is_new (bool, optional): Should a new record be created? Defaults to True.

    Returns:
        dict: Simulated form input.
    """
    recs = api.Records(token=conf.get_api_key())
    ddict = api.get_data_dict(token=conf.get_api_key())
    ppt_id = choice(list(recs.participants.records.keys()))
    while not recs.participants.records[ppt_id].appointments.records:
        ppt_id = choice(list(recs.participants.records.keys()))
    apt_id = choice(list(recs.participants.records[ppt_id].appointments.records.keys()))
    data = {
        "inputId": ppt_id,
        "inputAptId": "new" if is_new else apt_id,
        "inputStudy": choice(list(ddict["appointment_study"].keys())),
        "inputStatus": choice(list(ddict["appointment_status"].keys())),
        "inputDate": "2024-12-31 14:09",
        "inputTaxiAddress": generate_str(),
        "inputComments": ". ".join([generate_str(25) for _ in range(3)]),
    }
    data = {k: str(v) for k, v in data.items()}
    return data


def create_finput_que(is_new: bool = True) -> dict:
    """Simulate form input to test POST request in questionnaires.

    Args:
        is_new (bool, optional): Should a new record be created? Defaults to True.

    Returns:
        dict: Simulated form input.
    """
    recs = api.Records(token=conf.get_api_key())
    ddict = api.get_data_dict(token=conf.get_api_key())
    lang_exp = generate_lang_exp()
    ppt_id = choice(list(recs.participants.records.keys()))
    while not recs.participants.records[ppt_id].questionnaires.records:
        ppt_id = choice(list(recs.participants.records.keys()))
    que_id = choice(
        list(recs.participants.records[ppt_id].questionnaires.records.keys())
    )
    data = {
        "inputId": ppt_id,
        "inputQueId": "new" if is_new else que_id,
        "inputIsEstimated": choice(["0", "1"]),
        "inputLang1": choice(list(ddict["language_lang1"].keys())),
        "inputLang1Exp": lang_exp[0],
        "inputLang2": choice(list(ddict["language_lang1"].keys())),
        "inputLang2Exp": lang_exp[1],
        "inputLang3": choice(list(ddict["language_lang1"].keys())),
        "inputLang3Exp": lang_exp[2],
        "inputLang4": choice(list(ddict["language_lang1"].keys())),
        "inputLang4Exp": lang_exp[3],
        "inputComments": ". ".join([generate_str(25) for _ in range(3)]),
    }

    data = {k: str(v) for k, v in data.items()}
    return data


def create_record_ppt(is_new: bool = True) -> dict:
    """Create a REDCap participant record.

    Args:
        is_new (bool): Should a new record be created? Defaults to True.

    Returns:
        dict: A REDCap record.
    """
    recs = api.Records(token=conf.get_api_key())
    ppt_id = choice(list(recs.participants.records.keys()))
    return {
        "record_id": "0" if is_new else ppt_id,
        "participant_date_created": "2024-12-16 11:13:00",
        "participant_date_updated": "2024-12-16 11:13:00",
        "participant_name": generate_str(),
        "participant_age_created_months": choice(range(12)),
        "participant_age_created_days": choice(range(31)),
        "participant_days_since_last_apt": "",
        "participant_sex": str(choice(range(1, 6))),
        "participant_source": str(choice(range(1, 3))),
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


def create_record_apt(is_new: bool = True) -> dict:
    """Create a REDCap appointment record.

    Args:
        is_new (bool): Should a new record be created? Defaults to True.

    Returns:
        dict: A REDCap record.
    """
    token = conf.get_api_key()
    ddict = get_data_dict()
    recs = api.Records(token=token)
    ppd_id_list = list(recs.participants.records.keys())
    ppt_id = choice(ppd_id_list)
    apt_recs = recs.participants.records[ppt_id].appointments.records
    while not apt_recs:
        ppt_id = choice(ppd_id_list)
        apt_recs = recs.participants.records[ppt_id].appointments.records
    apt_id = choice(list(apt_recs.keys()))
    date_fmt = "%Y-%m-%d %H:%M:%S"
    return {
        "record_id": ppt_id,
        "redcap_repeat_instrument": "appointments",
        "redcap_repeat_instance": (
            api.get_next_id(token=token) if is_new else apt_id.split(":")[1]
        ),
        "appointment_study": choice(list(ddict["appointment_study"].keys())),
        "appointment_date_created": datetime.datetime.strptime(
            "2024-12-12 14:09:00", date_fmt
        ),
        "appointment_date_updated": datetime.datetime.strptime(
            "2024-12-14 12:08:00", date_fmt
        ),
        "appointment_date": datetime.datetime.strptime(
            "2024-12-31 14:09", "%Y-%m-%d %H:%M"
        ),
        "appointment_taxi_address": generate_str(),
        "appointment_taxi_isbooked": choice(["0", "1"]),
        "appointment_status": choice(list(ddict["appointment_status"].keys())),
        "appointment_comments": ". ".join([generate_str(25) for _ in range(3)]),
        "appointments_complete": "2",
    }


def create_record_que(is_new: bool = True) -> dict:
    """Create a REDCap questionnaire record.

    Args:
        is_new (bool): Should a new record be created? Defaults to True.

    Returns:
        dict: A REDCap record.
    """
    token = conf.get_api_key()
    ddict = get_data_dict()
    recs = api.Records(token=token)
    lang_exp = generate_lang_exp()
    ppt_id_list = list(recs.participants.records.keys())
    ppt_id = choice(ppt_id_list)
    que_recs = recs.participants.records[ppt_id].questionnaires.records
    while not que_recs:
        ppt_id = choice(ppt_id_list)
        que_recs = recs.participants.records[ppt_id].questionnaires.records
    que_id = choice(list(que_recs.keys()))

    date_fmt = "%Y-%m-%d %H:%M:%S"
    date = "2024-12-12 14:24:00"
    return {
        "record_id": ppt_id,
        "redcap_repeat_instrument": "language",
        "redcap_repeat_instance": (
            api.get_next_id(token=token) if is_new else que_id.split(":")[1]
        ),
        "language_date_created": datetime.datetime.strptime(date, date_fmt),
        "language_date_updated": datetime.datetime.strptime(date, date_fmt),
        "language_isestimated": choice(["0", "1"]),
        "language_lang1": choice(list(ddict["language_lang1"].keys())),
        "language_lang1_exp": lang_exp[0],
        "language_lang2": choice(list(ddict["language_lang2"].keys())),
        "language_lang2_exp": lang_exp[1],
        "language_lang3": choice(list(ddict["language_lang3"].keys())),
        "language_lang3_exp": lang_exp[2],
        "language_lang4": choice(list(ddict["language_lang4"].keys())),
        "language_lang4_exp": lang_exp[3],
        "language_comments": "",
        "language_complete": "2",
    }


def last_participant_added(records: api.Records = None) -> str:
    """Returns the record_id of the last record."""
    token = conf.get_api_key()
    if records is None:
        records = api.Records(token=token)
    return list(records.participants.records.keys())[-1]


def participant_exists(ppt_id: str, records: api.Records = None) -> bool:
    """Check that participant exists"""
    token = conf.get_api_key()
    if records is None:
        records = api.Records(token=token)
    try:
        api.get_participant(ppt_id, token=token)
        return True
    except api.RecordNotFound:
        return False
