"""
Util functions for the app.
"""

import os
from collections import OrderedDict
import datetime
import shutil
import pandas as pd
from pandas import DataFrame
from flask import flash, render_template
from babylab.src import api


def format_ppt_id(ppt_id: str) -> str:
    """Format appointment ID.

    Args:
        ppt_id (str): Participant ID.

    Returns:
        str: Formated participant ID.
    """
    return f"<a href=/participants/{ppt_id}>{ppt_id}</a>"


def format_apt_id(apt_id: str) -> str:
    """Format appointment ID.

    Args:
        apt_id (str): Appointment ID.

    Returns:
        str: Formated appointment ID.
    """
    return f"<a href=/appointments/{apt_id}>{apt_id}</a>"


def format_que_id(que_id: str, ppt_id: str) -> str:
    """Format questionnaire ID.

    Args:
        apt_id (str): Questionnaire ID.
        ppt_id (str): Participant ID.

    Returns:
        str: Formated questionnaire ID.
    """
    return f"<a href=/participants/{ppt_id}/questionnaires/{que_id}>{que_id}</a>"


def format_percentage(x: float | int) -> str:
    """Format number into percentage.

    Args:
        x (float | int): Number to format. Must be higher than or equal to zero, and lower than or equal to one.

    Raises:
        ValueError: If number is not higher than or equal to zero, and lower than or equal to one.

    Returns:
        str: Formatted percentage.
    """  # pylint: disable=line-too-long
    if x > 100 or x < 0:
        raise ValueError(
            "`x` higher than or equal to zero, and lower than or equal to one"
        )
    return str(int(float(x))) if x else ""


def format_status(status: str) -> str:
    """Format appointment status.

    Args:
        status (str): Appointment status value.

    Returns:
        str: Formated status value.
    """
    color_map = {
        "Scheduled": "black",
        "Confirmed": "orange",
        "Successful": "green",
        "Cancelled - Drop": "grey",
        "Cancelled - Reschedule": "red",
        "No show": "red",
    }
    return f"<p style='color: {color_map[status]};'>{status}</p>"


def format_taxi_isbooked(address: str, isbooked: str) -> str:
    """Format ``taxi_isbooked`` variable to HTML.

    Args:
        address (str): ``taxi_address`` value.
        isbooked (str): ``taxi_isbooked`` value.

    Raises:
        ValueError: If ``isbooked`` is not "0" or "1".

    Returns:
        str: Formatted HTML string.
    """  # pylint: disable=line-too-long
    if isbooked not in ["0", "1"]:
        raise ValueError("`is_booked` must be one of '0' or '1'")
    if not address:
        return ""
    if int(isbooked):
        return "<p style='color: green;'>Yes</p>"
    return "<p style='color: red;'>No</p>"


def format_modify_button(ppt_id: str, apt_id: str = None, ques_id: str = None):
    """Add modify button.

    Args:
        ppt_id (str): Participant ID.
        apt_id (str, optional): Appointment ID. Defaults to None.
        ques_id (str, optional): Questionnaire ID. Defaults to None.

    Returns:
        str: Formatted HTML string.
    """  # pylint: disable=line-too-long
    if apt_id:
        return f'<a href="/participants/{ppt_id}/{apt_id}/appointment_modify"><button type="button" class="btn btn-warning">Modify</button></a>'  # pylint: disable=line-too-long

    if ques_id:
        return f'<a href="/participants/{ppt_id}/questionnaires/{ques_id}/questionnaire_modify"><button type="button" class="btn btn-warning">Modify</button></a>'  # pylint: disable=line-too-long

    return f'<a href="/participants/{ppt_id}/participant_modify"><button type="button" class="btn btn-warning">Modify</button></a>'  # pylint: disable=line-too-long


def format_isestimated(isestimated: str) -> str:
    """Format ``isestimated`` variable.

    Args:
        isestimated (str): Value of ``isestimated`` variable.

    Returns:
        str: Formatted ``isestimated`` value.
    """
    return (
        "<p style='color: red;'>Estimated</p>"
        if isestimated == "1"
        else "<p style='color: green;'>Calculated</p>"
    )


def format_df(
    x: DataFrame,
    data_dict: dict,
    prefixes: list[str] = None,
) -> DataFrame:
    """Reformat dataframe.

    Args:
        x (DataFrame): Dataframe to reformat.
        data_dict (dict): Data dictionary to labels to use, as returned by ``api.get_data_dict``.
        prefixes (list[str]): List of prefixes to look for in variable names.

    Returns:
        DataFrame: A reformated Dataframe.
    """
    if prefixes is None:
        prefixes = ["participant", "appointment", "language"]
    for col_name, col_values in x.items():
        kdict = [x + "_" + col_name for x in prefixes]
        for k in kdict:
            if k in data_dict:
                x[col_name] = [data_dict[k][v] if v else "" for v in col_values]
        if "lang" in col_name:
            x[col_name] = ["" if v == "None" else v for v in x[col_name]]
        if "exp" in col_name:
            x[col_name] = [format_percentage(v) for v in col_values]
        if "taxi_isbooked" in col_name:
            pairs = zip(x["taxi_address"], x[col_name])
            x[col_name] = [format_taxi_isbooked(a, i) for a, i in pairs]
        if "isestimated" in col_name:
            x[col_name] = [format_isestimated(x) for x in x[col_name]]
    return x


def format_dict(x: dict, data_dict: dict) -> dict:
    """Reformat dictionary.

    Args:
        x (dict): dictionary to reformat.
        data_dict (dict): Data dictionary to labels to use, as returned by ``api.get_data_dict``.

    Returns:
        dict: A reformatted dictionary.
    """
    fields = ["participant_", "appointment_", "language_"]
    y = dict(x)
    for k, v in y.items():
        for f in fields:
            kdict = f + k
            if kdict in data_dict and v:
                y[k] = data_dict[kdict][v]
        if "exp" in k:
            y[k] = round(float(v), None) if v else ""
        if "taxi_isbooked" in k:
            y[k] = format_taxi_isbooked(y["taxi_address"], y[k])

    return y


def replace_labels(x: DataFrame | dict, data_dict: dict) -> DataFrame:
    """Replace field values with labels.

    Args:
        x (DataFrame): Pandas DataFrame in which to replace values with labels.
        data_dict (dict): Data dictionary as returned by ``get_data_dictionary``.

    Returns:
        DataFrame: A Pandas DataFrame with replaced labels.
    """  # pylint: disable=line-too-long
    if isinstance(x, DataFrame):
        return format_df(x, data_dict)
    if isinstance(x, dict):
        return format_dict(x, data_dict)
    return None


def get_participants_table(
    records: api.Records, data_dict: dict, n: int = None
) -> DataFrame:
    """Get participants table

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict, optional): Data dictionary as returned by ``api.get_data_dictionary``.
        n (int, optional): Number of records to show. Defaults to None (all records are shown).

    Returns:
        DataFrame: Table of partcicipants.
    """  # pylint: disable=line-too-long
    cols = [
        "name",
        "age_now_months",
        "age_now_days",
        "sex",
        "date_created",
        "date_updated",
    ]
    if not records.participants.records:
        return DataFrame([], columns=cols)

    new_age_months = []
    new_age_days = []
    for _, v in records.participants.records.items():
        age = api.get_age(
            birth_date=api.get_birth_date(
                age=f"{v.data['age_now_months']}:{v.data['age_now_days']}"
            )
        )
        new_age_months.append(int(age[0]))
        new_age_days.append(int(age[1]))

    df = records.participants.to_df()
    df["age_now_months"] = new_age_months
    df["age_now_days"] = new_age_days
    if n:
        df = df.tail(n)
    return replace_labels(df, data_dict)


def get_age_timestamp(
    apt_records: dict, ppt_records: dict, timestamp: str = "date"
) -> tuple[str, str]:
    """Get age at timestamp in months and days.

    Args:
        apt_records (dict): Appointment records.
        ppt_records (dict): Participant records.
        timestamp (str, optional): Timestamp at which to calculate age. Defaults to "date".

    Raises:
        ValueError: If tiemstamp is not "date" or "date_created".

    Returns:
        tuple[str, str]: Age at timestamp in months and days.
    """
    if timestamp not in ["date", "date_created"]:
        raise ValueError("timestamp must be 'date' or 'date_created'")
    date_format = "%Y-%m-%d %H:%M" if timestamp == "date" else "%Y-%m-%d %H:%M:%S"
    months_new = []
    days_new = []
    for v in apt_records.values():
        if timestamp == "date_created":
            t = datetime.datetime.strptime(
                ppt_records[v.record_id].data[timestamp],
                date_format,
            )
        else:
            t = datetime.datetime.strptime(
                v.data["date"],
                "%Y-%m-%d %H:%M",
            )
        months = ppt_records[v.record_id].data["age_now_months"]
        days = ppt_records[v.record_id].data["age_now_days"]
        age_now = api.get_age(
            birth_date=api.get_birth_date(age=f"{months}:{days}"),
            timestamp=t,
        )
        months_new.append(int(age_now[0]))
        days_new.append(int(age_now[1]))
    return months_new, days_new


def get_appointments_table(
    records: api.Records,
    data_dict: dict = None,
    ppt_id: str = None,
    study: str = None,
    n: int = None,
) -> DataFrame:
    """Get appointments table.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        ppt_id (str, optional): Participant ID. Defaults to None.
        study (str, optional): Study to filter for. Defaults to None.
        n (int, optional): Number of records to show. Defaults to None (all records are shown).

    Returns:
        DataFrame: Table of appointments.
    """  # pylint: disable=line-too-long
    apts = (
        records.participants.records[ppt_id].appointments
        if ppt_id
        else records.appointments
    )

    if study:
        apts.records = {
            k: v for k, v in apts.records.items() if v.data["study"] == study
        }

    if not apts.records:
        return DataFrame(
            [],
            columns=[
                "appointment_id",
                "record_id",
                "study",
                "status",
                "date",
                "date_created",
                "date_updated",
                "taxi_address",
                "taxi_isbooked",
            ],
        )
    apt_records = apts.records
    ppt_records = records.participants.records

    df = apts.to_df()
    df["appointment_id"] = df["id"]

    # get current age
    age_now = get_age_timestamp(apt_records, ppt_records, "date_created")[:n]
    df["age_now_months"] = age_now[0]
    df["age_now_days"] = age_now[1]

    # get age at appointment
    age_apt = get_age_timestamp(apt_records, ppt_records, "date")[:n]
    df["age_apt_months"] = age_apt[0]
    df["age_apt_days"] = age_apt[1]
    if n:
        df = df.tail(n)
    return replace_labels(df, data_dict)


def get_questionnaires_table(
    records: api.Records,
    data_dict: dict,
    ppt_id: str = None,
    n: int = None,
) -> DataFrame:
    """Get questionnaires table.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        ppt_id (str, optional): Participant ID. Defaults to None.
        study (str, optional): Study to filter for. Defaults to None.
        n (int, optional): Number of records to show. Defaults to None (all records are shown).

    Returns:
        DataFrame: A formated Pandas DataFrame.
    """  # pylint: disable=line-too-long
    if ppt_id is None:
        quest = records.questionnaires
    else:
        quest = records.participants.records[ppt_id].questionnaires

    if not quest.records:
        return DataFrame(
            [],
            columns=[
                "record_id",
                "questionnaire_id",
                "isestimated",
                "date_created",
                "date_updated",
                "lang1",
                "lang1_exp",
                "lang2",
                "lang2_exp",
                "lang3",
                "lang3_exp",
                "lang4",
                "lang4_exp",
            ],
        )
    df = quest.to_df()
    df["questionnaire_id"] = [
        str(p) + ":" + str(q) for p, q in zip(df.index, df["redcap_repeat_instance"])
    ]
    df = replace_labels(df, data_dict)
    if n:
        df = df.tail(n)
    return df


def count_col(
    x: DataFrame,
    col: str,
    values_sort: bool = False,
    cumulative: bool = False,
    missing_label: str = "Missing",
) -> dict:
    """Count frequencies of column in DataFrame.

    Args:
        x (DataFrame): DataFrame containing the target column.
        col (str): Name of the column.
        values_sort (str, optional): Should the resulting dict be ordered by values? Defaults to False.
        cumulative (bool, optional): Should the counts be cumulative? Defaults to False.
        missing_label (str, optional): Label to associate with missing values. Defaults to "Missing".

    Returns:
        dict: Counts of each category, sorted in descending order.
    """  # pylint: disable=line-too-long
    counts = x[col].value_counts().to_dict()
    counts = {missing_label if not k else k: v for k, v in counts.items()}
    counts = dict(sorted(counts.items()))
    if values_sort:
        counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    if cumulative:
        for idx, (k, v) in enumerate(counts.items()):
            if idx > 0:
                counts[k] = v + list(counts.values())[idx - 1]
    return counts


def prepare_dashboard(
    records: api.Records = None, data_dict: dict = None, **kwargs
) -> dict:
    """Prepare data for dashboard.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict, optional): Data dictionary as returned by ``api.get_data_dictionary``. Defaults to None.
        **kwargs: Extra arguments passed to ``get_participants_table``, ``get_appointments_table``, and ``get_questionnaires_table``

    Returns:
        dict: Parameters for the dashboard endpoint.
    """  # pylint: disable=line-too-long
    ppts = get_participants_table(records, data_dict=data_dict, **kwargs)
    apts = get_appointments_table(records, data_dict=data_dict, **kwargs)
    quest = get_questionnaires_table(records, data_dict=data_dict, **kwargs)
    ppts["age_days"] = round(
        ppts["age_now_days"] + (ppts["age_now_months"] * 30.437), None
    ).astype(int)
    age_bins = list(range(0, max(ppts["age_days"]), 15))
    labels = [f"{int(a // 30)}:{int(a % 30)}" for a in age_bins]
    ppts["age_days_binned"] = pd.cut(
        ppts["age_days"], bins=age_bins, labels=labels[:-1]
    )

    age_dist = count_col(ppts, "age_days_binned")
    sex_dist = count_col(ppts, "sex", values_sort=True)
    ppts_date_created = count_col(ppts, "date_created", cumulative=True)
    apts_date_created = count_col(apts, "date_created", cumulative=True)
    status_dist = count_col(apts, "status", values_sort=True)
    lang1_dist = count_col(quest, "lang1", values_sort=True, missing_label="None")
    lang2_dist = count_col(quest, "lang2", values_sort=True, missing_label="None")
    return {
        "n_ppts": ppts.shape[0],
        "n_apts": apts.shape[0],
        "age_dist_labels": list(age_dist.keys()),
        "age_dist_values": list(age_dist.values()),
        "sex_dist_labels": list(sex_dist.keys()),
        "sex_dist_values": list(sex_dist.values()),
        "ppts_date_created_labels": list(ppts_date_created.keys()),
        "ppts_date_created_values": list(ppts_date_created.values()),
        "apts_date_created_labels": list(apts_date_created.keys()),
        "apts_date_created_values": list(apts_date_created.values()),
        "status_dist_labels": list(status_dist.keys()),
        "status_dist_values": list(status_dist.values()),
        "lang1_dist_labels": list(lang1_dist.keys())[:24],
        "lang1_dist_values": list(lang1_dist.values())[:24],
        "lang2_dist_labels": list(lang2_dist.keys())[:24],
        "lang2_dist_values": list(lang2_dist.values())[:24],
    }


def prepare_participants(records: api.Records, data_dict: dict, **kwargs) -> dict:
    """Prepare data for participants page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        **kwargs: Extra arguments passed to ``get_participants_table``.

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = get_participants_table(records, data_dict=data_dict, **kwargs)
    classes = "table table-hover table-responsive"
    df["record_id"] = [format_ppt_id(i) for i in df.index]
    df.index = df.index.astype(int)
    df = df.sort_index(ascending=False)
    df["modify_button"] = [format_modify_button(p) for p in df.index]
    df = df[
        [
            "record_id",
            "name",
            "age_now_months",
            "age_now_days",
            "sex",
            "date_created",
            "date_updated",
            "modify_button",
        ]
    ]
    df = df.rename(
        columns={
            "record_id": "Participant",
            "name": "Name",
            "age_now_months": "Age (months)",
            "age_now_days": "Age (days)",
            "sex": "Sex",
            "date_created": "Added on",
            "date_updated": "Last updated",
            "modify_button": "",
        }
    )
    return {
        "table": df.to_html(
            classes=classes, escape=False, justify="left", index=False, bold_rows=True
        )
    }


def prepare_record_id(
    records: api.Records, data_dict: dict, ppt_id: str, **kwargs
) -> dict:
    """Prepare record ID page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        ppt_id (str, optional): Participant ID. Defaults to None.
        **kwargs: Extra arguments passed to ``get_participants_table``, ``get_appointments_table``, and ``get_questionnaires_table``

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    data = records.participants.records[ppt_id].data
    for k, v in data.items():
        kdict = "participant_" + k
        if kdict in data_dict:
            data[k] = data_dict[kdict][v] if v else ""
    data["age_now_months"] = (
        str(data["age_now_months"]) if data["age_now_months"] else ""
    )
    data["age_now_days"] = str(data["age_now_days"]) if data["age_now_days"] else ""
    data["parent1"] = data["parent1_name"] + " " + data["parent1_surname"]
    data["parent2"] = data["parent2_name"] + " " + data["parent2_surname"]

    classes = "table table-hover table-responsive"

    # prepare participants table
    df_appt = get_appointments_table(
        records, data_dict=data_dict, ppt_id=ppt_id, **kwargs
    )
    df_appt["record_id"] = [format_ppt_id(i) for i in df_appt.index]
    df_appt["appointment_id"] = [format_apt_id(i) for i in df_appt["appointment_id"]]
    df_appt = df_appt.sort_values(by="date", ascending=False)
    df_appt = df_appt[
        [
            "record_id",
            "appointment_id",
            "study",
            "date",
            "date_created",
            "date_updated",
            "taxi_address",
            "taxi_isbooked",
            "status",
        ]
    ]
    df_appt = df_appt.rename(
        columns={
            "record_id": "Participant",
            "appointment_id": "Appointment",
            "study": "Study",
            "date": "Date",
            "date_created": "Made on the",
            "date_updated": "Last update",
            "taxi_address": "Taxi address",
            "taxi_isbooked": "Taxi booked",
            "status": "Status",
        }
    )
    table_appt = df_appt.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    # prepare language questionnaires table
    df_quest = get_questionnaires_table(records, data_dict=data_dict, ppt_id=ppt_id)
    df_quest["questionnaire_id"] = [
        format_que_id(p, q)
        for p, q in zip(df_quest.index, df_quest["questionnaire_id"])
    ]
    df_quest["record_id"] = [format_ppt_id(i) for i in df_quest.index]
    df_quest = df_quest[
        [
            "questionnaire_id",
            "record_id",
            "lang1",
            "lang1_exp",
            "lang2",
            "lang2_exp",
            "lang3",
            "lang3_exp",
            "lang4",
            "lang4_exp",
            "date_created",
            "date_updated",
        ]
    ]
    df_quest = df_quest.sort_values("date_created", ascending=False)
    df_quest = df_quest.rename(
        columns={
            "record_id": "ID",
            "questionnaire_id": "Questionnaire",
            "date_updated": "Last updated",
            "date_created": "Created on the:",
            "lang1": "L1",
            "lang1_exp": "%",
            "lang2": "L2",
            "lang2_exp": "%",
            "lang3": "L3",
            "lang3_exp": "%",
            "lang4": "L4",
            "lang4_exp": "%",
        }
    )

    table_quest = df_quest.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    return {
        "data": data,
        "table_appointments": table_appt,
        "table_questionnaires": table_quest,
    }


def prepare_appointments(
    records: api.Records, data_dict: dict = None, study: str = None, **kwargs
):
    """Prepare record ID page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        study (str, optional): Study to filter for. Defaults to None.
        **kwargs: Extra arguments passed to ``get_participants_table``, ``get_appointments_table``, and ``get_questionnaires_table``

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = get_appointments_table(records, data_dict=data_dict, study=study, **kwargs)
    classes = "table table-hover table-responsive"
    df["record_id"] = [format_ppt_id(i) for i in df.index]
    df["modify_button"] = [
        format_modify_button(p, a) for p, a in zip(df.index, df["appointment_id"])
    ]
    df["appointment_id"] = [format_apt_id(i) for i in df["appointment_id"]]
    df["status"] = [format_status(s) for s in df["status"]]

    df = df[
        [
            "appointment_id",
            "record_id",
            "study",
            "status",
            "date",
            "date_created",
            "date_updated",
            "taxi_address",
            "taxi_isbooked",
            "modify_button",
        ]
    ]
    df = df.sort_values("date_updated", ascending=False)

    df = df.rename(
        columns={
            "appointment_id": "Appointment",
            "record_id": "Participant",
            "study": "Study",
            "status": "Appointment status",
            "date": "Date",
            "date_created": "Made on the",
            "date_updated": "Last updated",
            "taxi_address": "Taxi address",
            "taxi_isbooked": "Taxi booked",
            "modify_button": "",
        }
    )

    table = df.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    return {"table": table}


def prepare_questionnaires(records: api.Records, data_dict: dict, **kwargs):
    """Prepare appointments page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        **kwargs: Extra arguments passed to ``get_participants_table``, ``get_appointments_table``, and ``get_questionnaires_table``

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = get_questionnaires_table(records, data_dict=data_dict, **kwargs)
    classes = "table table-hover"
    df["modify_button"] = [
        format_modify_button(p, ques_id=q)  # pylint: disable=line-too-long
        for p, q in zip(df.index, df["questionnaire_id"])
    ]
    df["questionnaire_id"] = [
        format_que_id(p, q) for p, q in zip(df["questionnaire_id"], df.index)
    ]
    df["record_id"] = [format_ppt_id(i) for i in df.index]
    df = df[
        [
            "questionnaire_id",
            "record_id",
            "isestimated",
            "lang1",
            "lang1_exp",
            "lang2",
            "lang2_exp",
            "lang3",
            "lang3_exp",
            "lang4",
            "lang4_exp",
            "date_updated",
            "date_created",
            "modify_button",
        ]
    ]
    df = df.sort_values("date_created", ascending=False)
    df = df.rename(
        columns={
            "record_id": "Participant",
            "questionnaire_id": "Questionnaire",
            "isestimated": "Status",
            "date_updated": "Last updated",
            "date_created": "Added on the:",
            "lang1": "L1",
            "lang1_exp": "%",
            "lang2": "L2",
            "lang2_exp": "%",
            "lang3": "L3",
            "lang3_exp": "%",
            "lang4": "L4",
            "lang4_exp": "%",
            "modify_button": "",
        }
    )

    table = df.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    return {"table": table}


def prepare_studies(records: api.Records, data_dict: dict, study: str = None):
    """Prepare appointments page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        study (str, optional): Study to filter for. Defaults to None.

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = get_appointments_table(records, data_dict=data_dict, study=study)
    classes = "table table-hover table-responsives"
    df["appointment_id"] = [format_apt_id(i) for i in df["appointment_id"]]
    df["record_id"] = [format_ppt_id(i) for i in df.index]
    df = df[
        [
            "appointment_id",
            "record_id",
            "study",
            "date",
            "date_created",
            "date_updated",
            "taxi_address",
            "taxi_isbooked",
            "status",
        ]
    ]
    df = df.sort_values("date", ascending=False)

    df = df.rename(
        columns={
            "appointment_id": "Appointment",
            "record_id": "Participant",
            "study": "Study",
            "date": "Date",
            "date_created": "Made on the",
            "date_updated": "Last updated",
            "taxi_address": "Taxi address",
            "taxi_isbooked": "Taxi booked",
            "status": "Appointment status",
        }
    )

    table = df.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    date = df["Date"].value_counts().to_dict()
    date = OrderedDict(sorted(date.items()))
    for idx, (k, v) in enumerate(date.items()):
        if idx > 0:
            date[k] = v + list(date.values())[idx - 1]

    return {
        "n_apts": df.shape[0],
        "date_labels": list(date.keys()),
        "date_values": list(date.values()),
        "table": table,
    }


def clean_tmp(path: str = "tmp"):
    """Clean temporal directory

    Args:
        path (str, optional): Path to the temporal directory. Defaults to "tmp".
    """
    if os.path.exists(path):
        shutil.rmtree(path)


def prepare_email(ppt_id: str, apt_id: str, data: dict, data_dict: dict) -> dict:
    """Prepare email to send.

    Args:
        ppt_id (str): Participant ID.
        apt_id (str): Appointment ID.
        data (dict): Appointment data.

    Returns:
        dict: Email data.
    """
    email = {
        "record_id": ppt_id,
        "id": apt_id,
        "status": data["status"],
        "date": datetime.datetime.strptime(data["date"], "%Y-%m-%d %H:%M").isoformat(),
        "study": data["study"],
        "taxi_address": data["taxi_address"],
        "taxi_isbooked": data["taxi_isbooked"],
        "comments": data["comments"],
    }
    return replace_labels(email, data_dict)


def send_email_or_exception(email_from: str, **kwargs) -> None:
    """Try sending an email or catch the exception.

    Args:
        **kwargs: Arguments passed to ``prepare_email``.
    """
    try:
        data = prepare_email(**kwargs)
        api.send_email(data=data, email_from=email_from)
    except api.MailDomainException as e:
        flash(f"Appointment modified, but e-mail was not sent: {e}", "warning")
        return render_template("apt_new.html", **kwargs)
    except api.MailAddressException as e:
        flash(f"Appointment modified, but e-mail was not sent: {e}", "warning")
        return render_template("apt_new.html", **kwargs)
    return None


def create_event_or_exception(account: str, calendar_name: str, **kwargs) -> None:
    """Try creating and email or catch the exception.

    Args:
        **kwargs: Arguments passed to ``prepare_email``.
    """
    try:
        data = prepare_email(**kwargs)
        api.create_event(data=data, account=account, calendar_name=calendar_name)
    except api.MailDomainException as e:
        flash(f"Appointment created, but event was not created: {e}", "warning")
        return render_template("apt_new.html", **kwargs)
    except api.MailAddressException as e:
        flash(f"Appointment created, but event was not created: {e}", "warning")
        return render_template("apt_new.html", **kwargs)
    return None


def modify_event_or_exception(account: str, calendar_name: str, **kwargs) -> None:
    """Try modifying and email or catch the exception.

    Args:
        **kwargs: Arguments passed to ``prepare_email``.
    """
    try:
        data = prepare_email(**kwargs)
        api.modify_event(data=data, account=account, calendar_name=calendar_name)
    except api.MailDomainException as e:
        flash(f"Appointment modified, but event was not created: {e}", "warning")
        return render_template("apt_new.html", **kwargs)
    except api.MailAddressException as e:
        flash(f"Appointment modified, but event was not created: {e}", "warning")
        return render_template("apt_new.html", **kwargs)
    return None
