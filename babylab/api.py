#!/usr/bin/env python

"""
Functions to interact with the RedCAP API.
"""

import json
import zipfile
import os
from datetime import datetime
from collections import OrderedDict
import requests


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
        options = v["select_choices_or_calculations"].split("|")
        options_parsed = {}
        for o in options:
            x = o.split(", ")
            options_parsed[x[0]] = x[1].strip()
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
