"""Participants routes."""

from datetime import datetime
import requests
from flask import flash, redirect, render_template, url_for, request
from babylab.src import api, utils
from babylab.app import config as conf


def prepare_ppt(records: api.Records, data_dict: dict, **kwargs) -> dict:
    """Prepare data for participants page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        **kwargs: Extra arguments passed to ``get_participants_table``.

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = utils.get_ppt_table(records, data_dict=data_dict, **kwargs)
    classes = "table table-hover table-responsive"
    df["record_id"] = [utils.fmt_ppt_id(i) for i in df.index]
    df.index = df.index.astype(int)
    df = df.sort_index(ascending=False)
    df["buttons"] = [
        utils.fmt_modify_button(p)
        + " "
        + utils.fmt_new_button(record="Appointment", ppt_id=p)
        + " "
        + utils.fmt_new_button(record="Questionnaire", ppt_id=p)
        for p in df.index
    ]

    df = df[
        [
            "record_id",
            "name",
            "age_now_months",
            "age_now_days",
            "sex",
            "source",
            "email1",
            "phone1",
            "buttons",
        ]
    ]

    return {
        "table": df.to_html(
            classes=f'{classes}" id = "ppttable',
            escape=False,
            justify="left",
            index=False,
            bold_rows=True,
        )
    }


def prepare_record_id(ppt: api.Participant, data_dict: dict) -> dict:
    """Prepare record ID page.

    Args:
        records (api.Records): REDCap record of the participant, as returned by ``api.get_participant``.

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    data = ppt.data
    for k, v in data.items():
        kdict = "participant_" + k
        if kdict in data_dict:
            data[k] = data_dict[kdict][v] if v else ""
    age_created = (data["age_created_months"], data["age_created_days"])
    ts = datetime.strptime(data["date_created"], "%Y-%m-%d %H:%M:%S")
    age = api.get_age(age_created, ts)
    data["age_now_months"], data["age_now_days"] = str(age[0]), str(age[1])
    data["parent1"] = data["parent1_name"] + " " + data["parent1_surname"]
    data["parent2"] = data["parent2_name"] + " " + data["parent2_surname"]

    classes = "table table-hover table-responsive"

    # prepare participants table
    df_apt = utils.get_apt_table(ppt, data_dict=data_dict)
    df_apt["record_id"] = [utils.fmt_ppt_id(i) for i in df_apt.index]
    df_apt["appointment_id"] = [utils.fmt_apt_id(i) for i in df_apt["appointment_id"]]
    df_apt = df_apt.sort_values(by="date", ascending=False)
    df_apt = df_apt[
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
    df_apt = df_apt.rename(
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
    table_apt = df_apt.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    # prepare language questionnaires table
    df_que = utils.get_que_table(ppt, data_dict=data_dict)
    df_que["questionnaire_id"] = [
        utils.fmt_que_id(q) for q in df_que["questionnaire_id"]
    ]
    df_que["record_id"] = [utils.fmt_ppt_id(i) for i in df_que.index]
    df_que = df_que[
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
    df_que = df_que.sort_values("date_created", ascending=False)
    df_que = df_que.rename(
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

    table_que = df_que.to_html(
        classes=classes,
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    return {
        "data": data,
        "table_appointments": table_apt,
        "table_questionnaires": table_que,
    }


def ppt_routes(app):
    """Participants routes."""

    @app.route("/participants/")
    @conf.token_required
    def ppt_all(ppt_list: list[str] = None):
        """Participants database"""
        token = app.config["API_KEY"]
        records = app.config["RECORDS"]
        data_dict = api.get_data_dict(token=token)
        data = prepare_ppt(records, data_dict=data_dict)
        if ppt_list is None:
            ppt_list = list(records.participants.to_df().index)
            ppt_list = [int(x) for x in ppt_list]
            ppt_list.sort(reverse=True)
            ppt_list = [str(x) for x in ppt_list]

        return render_template(
            "ppt_all.html",
            ppt_options=ppt_list,
            data=data,
            data_dict=data_dict,
            n_ppt=len(records.participants.records),
        )

    @app.route("/participants/<string:ppt_id>", methods=["GET", "POST"])
    @conf.token_required
    def ppt(ppt_id: str):
        """Show the ppt_id for that participant"""
        token = app.config["API_KEY"]
        data_dict = api.get_data_dict(token=token)
        ppt = api.get_participant(ppt_id, token=token)
        data = prepare_record_id(ppt, data_dict)
        if request.method == "POST":
            try:
                api.delete_participant(data={"record_id": ppt_id}, token=token)
                flash("Participant deleted!", "success")
                app.config["RECORDS"] = conf.get_records_or_index(token=token)
                return redirect(url_for("ppt_all", records=app.config["RECORDS"]))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("ppt_all"))
        return render_template("ppt.html", ppt_id=ppt_id, data=data)

    @app.route("/participant_new", methods=["GET", "POST"])
    @conf.token_required
    def ppt_new():
        """New participant page"""
        token = app.config["API_KEY"]
        data_dict = api.get_data_dict(token=token)
        ppt_id = api.get_next_id(token=token)
        if request.method == "POST":
            finput = request.form
            date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            data = {
                "record_id": "0",
                "participant_date_created": date_now,
                "participant_date_updated": date_now,
                "participant_source": finput["inputSource"],
                "participant_name": finput["inputName"],
                "participant_age_created_months": finput["inputAgeMonths"],
                "participant_age_created_days": finput["inputAgeDays"],
                "participant_sex": finput["inputSex"],
                "participant_twin": finput["inputTwinID"],
                "participant_parent1_name": finput["inputParent1Name"],
                "participant_parent1_surname": finput["inputParent1Surname"],
                "participant_parent2_name": finput["inputParent2Name"],
                "participant_parent2_surname": finput["inputParent2Surname"],
                "participant_email1": finput["inputEmail1"],
                "participant_phone1": finput["inputPhone1"],
                "participant_email2": finput["inputEmail2"],
                "participant_phone2": finput["inputPhone2"],
                "participant_address": finput["inputAddress"],
                "participant_city": finput["inputCity"],
                "participant_postcode": finput["inputPostcode"],
                "participant_birth_type": finput["inputDeliveryType"],
                "participant_gest_weeks": finput["inputGestationalWeeks"],
                "participant_birth_weight": finput["inputBirthWeight"],
                "participant_head_circumference": finput["inputHeadCircumference"],
                "participant_apgar1": finput["inputApgar1"],
                "participant_apgar2": finput["inputApgar2"],
                "participant_apgar3": finput["inputApgar3"],
                "participant_hearing": finput["inputNormalHearing"],
                "participant_diagnoses": finput["inputDiagnoses"],
                "participant_comments": finput["inputComments"],
                "participants_complete": "2",
            }
            try:
                api.add_participant(data, modifying=False, token=token)
                flash(f"Participant added! ({ ppt_id })", "success")
                app.config["RECORDS"] = conf.get_records_or_index(token=token)
                return redirect(url_for("que_new", ppt_id=ppt_id))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("ppt_new", data_dict=data_dict))
        return render_template("ppt_new.html", data_dict=data_dict)

    @app.route(
        "/participants/<string:ppt_id>/participant_modify", methods=["GET", "POST"]
    )
    @conf.token_required
    def ppt_modify(ppt_id: str, data: dict = None, data_dict: dict = None):
        """Modify participant page"""
        token = app.config["API_KEY"]
        if data_dict is None:
            data_dict = api.get_data_dict(token=token)
        ppt = api.get_participant(ppt_id, token=token)
        if request.method == "POST":
            finput = request.form
            date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            data = {
                "record_id": ppt_id,
                "participant_date_updated": date_now,
                "participant_name": finput["inputName"],
                "participant_sex": finput["inputSex"],
                "participant_source": finput["inputSource"],
                "participant_twin": finput["inputTwinID"],
                "participant_parent1_name": finput["inputParent1Name"],
                "participant_parent1_surname": finput["inputParent1Surname"],
                "participant_parent2_name": finput["inputParent2Name"],
                "participant_parent2_surname": finput["inputParent2Surname"],
                "participant_email1": finput["inputEmail1"],
                "participant_phone1": finput["inputPhone1"],
                "participant_email2": finput["inputEmail2"],
                "participant_phone2": finput["inputPhone2"],
                "participant_address": finput["inputAddress"],
                "participant_city": finput["inputCity"],
                "participant_postcode": finput["inputPostcode"],
                "participant_birth_type": finput["inputDeliveryType"],
                "participant_gest_weeks": finput["inputGestationalWeeks"],
                "participant_birth_weight": finput["inputBirthWeight"],
                "participant_head_circumference": finput["inputHeadCircumference"],
                "participant_apgar1": finput["inputApgar1"],
                "participant_apgar2": finput["inputApgar2"],
                "participant_apgar3": finput["inputApgar3"],
                "participant_hearing": finput["inputNormalHearing"],
                "participant_diagnoses": finput["inputDiagnoses"],
                "participant_comments": finput["inputComments"],
                "participants_complete": "2",
            }
            try:
                api.add_participant(data, modifying=True, token=token)
                app.config["RECORDS"] = conf.get_records_or_index(token=token)
                flash("Participant modified!", "success")
                return redirect(url_for("ppt", ppt_id=ppt_id))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return render_template(
                    "ppt_modify.html", ppt_id=ppt_id, data=data, data_dict=data_dict
                )
        return render_template(
            "ppt_modify.html", ppt_id=ppt_id, data=ppt.data, data_dict=data_dict
        )
