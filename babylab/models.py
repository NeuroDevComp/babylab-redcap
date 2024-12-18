#!/usr/bin/env python

"""
REDCap database models and classes.
"""
import re
from dataclasses import dataclass
import pandas as pd
from babylab import api


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

        records = api.get_records(**kwargs)
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
