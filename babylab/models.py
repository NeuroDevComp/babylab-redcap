#!/usr/bin/env python

"""
Functions to interact with the RedCAP API
"""
import re
import json
import zipfile
import os
from datetime import datetime
from collections import OrderedDict
from dataclasses import dataclass
import requests
import pandas as pd


def post_request(
    fields: dict,
    token: str,
    timeout: int = (5, 10),
) -> dict:
    """Make a POST request to the REDCap database.

    Args:
        fields (dict): Fields to retrieve.
        token (str): API token.
        timeout (int, optional): Timeout of HTTP request in seconds. Defaults to 10.

    Raises:
        ValueError: If API token contains non-alphanumeric characters.

    Returns:
        dict: HTTP request response in JSON format.
    """
    fields = OrderedDict(fields)
    fields["token"] = token
    fields.move_to_end("token", last=False)
    if not token.isalnum():
        raise ValueError("Token contains non-alphanumeric characters")
    r = requests.post(
        "https://apps.sjdhospitalbarcelona.org/redcap/api/",
        data=fields,
        timeout=timeout,
    )
    r.raise_for_status()
    return r


def get_redcap_version(**kwargs) -> str:
    """Get REDCap version.
    Args:
        **kwargs: Arguments passed to ``post_request``.
    Returns:
        str: REDCAp version number.
    """
    fields = {
        "content": "version",
    }
    try:
        r = post_request(fields=fields, **kwargs)
        return r.content.decode("utf-8")
    except requests.exceptions.HTTPError as e:
        return print(e)


def get_data_dict(**kwargs):
    """Get data dictionaries for categorical variables

    Returns:
        **kwargs: Additional arguments passed tp ``post_request``.
    """
    items = [
        "participant_sex",
        "participant_birth_type",
        "participant_hearing",
        "appointment_study",
        "appointment_status",
        "language_lang1",
        "language_lang2",
        "language_lang3",
        "language_lang4",
    ]
    fields = {
        "content": "metadata",
        "format": "json",
        "returnFormat": "json",
    }

    for idx, i in enumerate(items):
        fields[f"fields[{idx}]"] = i
    r = json.loads(post_request(fields=fields, **kwargs).text)
    dicts = {}
    for k, v in zip(items, r):
        options = v["select_choices_or_calculations"].split(" | ")
        options_parsed = {}
        for o in options:
            x = o.split(", ")
            options_parsed[x[0]] = x[1]
        dicts[k] = options_parsed
    return dicts


def get_records(**kwargs):
    """Return records as JSON.

    Args:
        kwargs (str): Additional arguments passed to ``post_request``.

    Returns:
        dict: REDCap records in JSON format.
    """
    fields = {
        "content": "record",
        "format": "json",
        "type": "flat",
    }
    records = post_request(fields=fields, **kwargs).json()
    for r in records:
        for k, v in r.items():
            if "date" in k and v:
                try:
                    r[k] = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    r[k] = datetime.strptime(v, "%Y-%m-%d %H:%M")
    return records


def add_participant(data: dict, modifying: bool = False, **kwargs):
    """Add new participant to REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
        *kwargs: Additional arguments passed to ``post_request``.
    """
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "normal" if modifying else "overwrite",
        "forceAutoNumber": "false" if modifying else "true",
        "data": f"[{json.dumps(data)}]",
    }
    return post_request(fields=fields, **kwargs)


def add_appointment(data: dict, **kwargs):
    """Add new appointment to REDCap database.

    Args:
        record_id (dict): ID of participant.
        data (dict): Appointment data.
        *kwargs: Additional arguments passed to ``post_request``.
    """
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "overwrite",
        "forceAutoNumber": "false",
        "data": f"[{json.dumps(data)}]",
    }
    return post_request(fields=fields, **kwargs)


def add_questionnaire(data: dict, **kwargs):
    """Add new appointment to REDCap database.

    Args:
        data (dict): Questionnaire data.
        *kwargs: Additional arguments passed to ``post_request``.
    """
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "overwrite",
        "forceAutoNumber": "false",
        "data": f"[{json.dumps(data)}]",
    }

    return post_request(fields=fields, **kwargs)


def redcap_backup(file: str = "tmp/backup.zip", **kwargs) -> dict:
    """Download a backup of the REDCap database

    Args:
        file (str, optional): Output file, with .json extension. Defaults to None.

    Raises:
        ValueError: If ``file`` does not have the .json extension.

    Returns:
        dict: A dictionary with the key data and metadata of the project.
    """
    project = json.loads(
        post_request(
            fields={"content": "project", "format": "json", "returnFormat": "json"},
            **kwargs,
        ).text
    )
    fields = json.loads(
        post_request(
            fields={
                "content": "metadata",
                "format": "json",
                "returnFormat": "json",
            },
            **kwargs,
        ).text
    )
    instruments = json.loads(
        post_request(
            fields={"content": "instrument", "format": "json", "returnFormat": "json"},
            **kwargs,
        ).text
    )
    records = get_records(**kwargs)
    for r in records:
        for k, v in r.items():
            if isinstance(v, datetime):
                r[k] = datetime.strftime(v, "%Y-%m-%d %H:%M")
    backup = {
        "project": project,
        "instruments": instruments,
        "fields": fields,
        "records": records,
    }
    dname = os.path.dirname(file)
    if not os.path.exists(dname):
        os.makedirs(dname)
    for k, v in backup.items():
        fpath = dname + "/" + k + ".json"
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(v, f)
    for root, _, files in os.walk(dname, topdown=False):
        with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                if f.endswith(".json"):
                    z.write(root + "/" + f)
    return file


class Participant:
    """Participant in database"""

    def __init__(self, data):
        data = {
            re.sub("participant_", "", k): v
            for k, v in data.items()
            if k.startswith("participant_") or k == "record_id"
        }
        self.record_id = data["record_id"]
        self.data = data

    def __repr__(self):
        return f" Participant {self.record_id}"

    def __str__(self):
        return f" Participant {self.record_id}"


class Appointment:
    """Appointment in database"""

    def __init__(self, data):
        data = {
            re.sub("appointment_", "", k): v
            for k, v in data.items()
            if k.startswith("appointment_")
            or k in ["record_id", "redcap_repeat_instance"]
        }
        self.record_id = data["record_id"]
        self.data = data
        self.appointment_id = (
            data["record_id"] + ":" + str(data["redcap_repeat_instance"])
        )
        self.status = data["status"]
        self.date = data["date"]

    def __repr__(self):
        return f"Appointment {self.appointment_id}, participant {self.record_id}, {self.date}, {self.status}"  # pylint: disable=line-too-long

    def __str__(self):
        return f"Appointment {self.appointment_id}, participant {self.record_id}, {self.date}, {self.status}"  # pylint: disable=line-too-long


class Questionnaire:
    """Language questionnaire in database"""

    def __init__(self, data):
        data = {
            re.sub("language_", "", k): v
            for k, v in data.items()
            if k.startswith("language_") or k in ["record_id", "redcap_repeat_instance"]
        }
        self.record_id = data["record_id"]
        self.questionnaire_id = (
            data["record_id"] + ":" + str(data["redcap_repeat_instance"])
        )
        self.isestimated = data["isestimated"]
        self.data = data
        for i in range(1, 5):
            l = f"lang{i}_exp"
            self.data[l] = int(self.data[l]) if self.data[l] else 0

    def __repr__(self):
        return (
            f" Language questionnaire {self.questionnaire_id} from participant {self.record_id}"  # pylint: disable=no-member
            + f"\n- L1 ({self.data['lang1']}) = {self.data['lang1_exp']}%"
            + f"\n- L2 ({self.data['lang2']}) = {self.data['lang2_exp']}%"
            + f"\n- L3 ({self.data['lang3']}) = {self.data['lang3_exp']}%"
            + f"\n- L4 ({self.data['lang4']}) = {self.data['lang4_exp']}%"
        )  # pylint: disable=line-too-long

    def __str__(self):
        return (
            f" Language questionnaire {self.questionnaire_id} from participant {self.record_id}"  # pylint: disable=no-member
            + f"\n- L1 ({self.data['lang1']}) = {self.data['lang1_exp']}%"
            + f"\n- L2 ({self.data['lang2']}) = {self.data['lang2_exp']}%"
            + f"\n- L3 ({self.data['lang3']}) = {self.data['lang3_exp']}%"
            + f"\n- L4 ({self.data['lang4']}) = {self.data['lang4_exp']}%"
        )  # pylint: disable=line-too-long


@dataclass
class RecordList:
    """List of records"""

    records: dict

    def to_df(self) -> pd.DataFrame:
        """Transform a dictionary dataset to a Pandas DataFrame.
        Returns:
        pd.DataFrame: Tabular dataset.
        """
        db_list = []
        for v in self.records.values():
            d = pd.DataFrame(v.data.items())
            d = d.set_index([0])
            db_list.append(d.transpose())
        df = pd.concat(db_list)
        df.index = pd.Index(df[df.columns[0]])
        df = df[df.columns[1:]]
        return df


class Records:
    """RedCAP records"""

    def __init__(self, **kwargs):

        records = get_records(**kwargs)
        participants = {}
        appointments = {}
        questionnaires = {}
        for r in records:
            if r["redcap_repeat_instance"] and r["appointment_status"]:
                r["appointment_id"] = (
                    r["record_id"] + ":" + str(r["redcap_repeat_instance"])
                )
                appointments[r["appointment_id"]] = Appointment(r)
            if r["redcap_repeat_instance"] and r["language_lang1"]:
                r["questionnaire_id"] = (
                    r["record_id"] + ":" + str(r["redcap_repeat_instance"])
                )
                questionnaires[r["questionnaire_id"]] = Questionnaire(r)
            if not r["redcap_repeat_instrument"]:
                participants[r["record_id"]] = Participant(r)

        # add appointments and questionnaires to each participant
        for p, v in participants.items():
            apps = {k: v for k, v in appointments.items() if v.record_id == p}
            v.appointments = RecordList(apps)
            ques = {k: v for k, v in questionnaires.items() if v.record_id == p}
            v.questionnaires = RecordList(ques)

        self.participants = RecordList(participants)
        self.appointments = RecordList(appointments)
        self.questionnaires = RecordList(questionnaires)

    def __repr__(self):
        return (
            "RedCAP database:"
            + f"\n- {len(self.participants.records)} participants"
            + f"\n- {len(self.appointments.records)} appointments"
            + f"\n- {len(self.questionnaires.records)} language questionnaires"  # pylint: disable=line-too-long
        )

    def __str__(self):
        return (
            "RedCAP database:"
            + f"\n- {len(self.participants.records)} participants"
            + f"\n- {len(self.appointments.records)} appointments"
            + f"\n- {len(self.questionnaires.records)} language questionnaires"  # pylint: disable=line-too-long
        )
