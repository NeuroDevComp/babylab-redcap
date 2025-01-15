"""Participants routes."""

import datetime
import requests
from flask import flash, redirect, render_template, url_for, request
from babylab.src import api, utils
from babylab.app import config as conf


def participants_routes(app):
    """Participants routes."""

    @app.route("/participants/", methods=["GET", "POST"])
    @conf.token_required
    def ppt_all(
        ppt_id: str = None,
        ppt_options: list[str] = None,
        data_ppt: dict = None,
    ):
        """Participants database"""
        token = app.config["API_KEY"]
        records = conf.get_records_or_index(token=token)
        data_dict = api.get_data_dict(token=token)
        data = utils.prepare_participants(records, data_dict=data_dict, n=20)
        if ppt_options is None:
            ppt_options = list(records.participants.to_df().index)
            ppt_options = [int(x) for x in ppt_options]
            ppt_options.sort(reverse=True)
            ppt_options = [str(x) for x in ppt_options]
        if request.method == "POST":
            ppt_id = request.form["inputPptId"]
            if ppt_id != "-- Select one --":
                data_ppt = records.participants.records[ppt_id]
                return render_template(
                    "ppt_all.html",
                    data=data,
                    ppt_options=ppt_options,
                    data_dict=data_dict,
                    ppt_id=ppt_id,
                    data_ppt=data_ppt,
                )
        return render_template(
            "ppt_all.html",
            ppt_options=ppt_options,
            data=data,
            data_dict=data_dict,
            ppt_id=ppt_id,
            data_ppt=data_ppt,
            n_ppt=len(records.participants.records),
        )

    @app.route("/participants/<string:ppt_id>", methods=["GET", "POST"])
    @conf.token_required
    def ppt(ppt_id: str):
        """Show the ppt_id for that participant"""
        token = app.config["API_KEY"]
        data_dict = api.get_data_dict(token=token)
        records = conf.get_records_or_index(token=token)
        data = utils.prepare_record_id(records, data_dict, ppt_id)
        if request.method == "POST":
            try:
                api.delete_participant(
                    data={"record_id": ppt_id},
                    token=app.config["API_KEY"],
                )
                flash("Participant deleted!", "success")
                return redirect(url_for("ppt_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("ppt_all"))
        return render_template(
            "ppt.html",
            ppt_id=ppt_id,
            data=data,
        )

    @app.route("/participant_new", methods=["GET", "POST"])
    @conf.token_required
    def ppt_new():
        """New participant page"""
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        if request.method == "POST":
            finput = request.form
            date_now = datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M"
            )
            data = {
                "record_id": "0",
                "participant_date_created": date_now,
                "participant_date_updated": date_now,
                "participant_name": finput["inputName"],
                "participant_age_now_months": finput["inputAgeMonths"],
                "participant_age_now_days": finput["inputAgeDays"],
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
                api.add_participant(
                    data,
                    modifying=False,
                    token=app.config["API_KEY"],
                )
                flash("Participant added!", "success")
                return redirect(url_for("ppt_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("ppt_new", data_dict=data_dict))
        return render_template("ppt_new.html", data_dict=data_dict)

    @app.route(
        "/participants/<string:ppt_id>/participant_modify", methods=["GET", "POST"]
    )
    @conf.token_required
    def ppt_modify(
        ppt_id: str,
        data: dict = None,
    ):
        """Modify participant page"""
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        data = (
            api.Records(token=app.config["API_KEY"]).participants.records[ppt_id].data
        )
        if request.method == "POST":
            finput = request.form
            date_now = datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M"
            )
            data = {
                "record_id": ppt_id,
                # "participant_date_added": date_now,
                "participant_date_updated": date_now,
                "participant_name": finput["inputName"],
                "participant_age_now_months": finput["inputAgeMonths"],
                "participant_age_now_days": finput["inputAgeDays"],
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
                api.add_participant(
                    data,
                    modifying=True,
                    token=app.config["API_KEY"],
                )
                return redirect(url_for("ppt", ppt_id=ppt_id))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return render_template(
                    "ppt_modify.html", ppt_id=ppt_id, data=data, data_dict=data_dict
                )
        return render_template(
            "ppt_modify.html", ppt_id=ppt_id, data=data, data_dict=data_dict
        )
