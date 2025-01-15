"""Questionnaires routes."""

import datetime
import requests
from flask import flash, redirect, render_template, url_for, request
from babylab.src import api, utils
from babylab.app import config as conf


def questionnaires_routes(app):
    """Questionnaire routes."""

    @app.route("/questionnaires/")
    @conf.token_required
    def que_all():
        """Participants database"""
        records = api.Records(token=app.config["API_KEY"])
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        data = utils.prepare_questionnaires(records, data_dict=data_dict, n=20)
        return render_template(
            "que_all.html",
            data=data,
            data_dict=data_dict,
            n_que=len(records.questionnaires.records),
        )

    @app.route(
        "/participants/<string:ppt_id>/questionnaires/<string:que_id>",
        methods=["GET", "POST"],
    )
    @conf.token_required
    def que(
        ppt_id: str = None,
        que_id: str = None,
        data: dict = None,
    ):
        """Show a language questionnaire"""
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        try:
            records = api.Records(token=app.config["API_KEY"])
        except Exception:  # pylint: disable=broad-exception-caught
            return render_template("index.html", login_status="incorrect")
        data = records.questionnaires.records[que_id].data
        data = utils.replace_labels(data, data_dict=data_dict)
        if request.method == "POST":
            try:
                ppt_id, que_id = que_id.split(":")
                api.delete_questionnaire(
                    data={"record_id": ppt_id, "redcap_repeat_instance": que_id},
                    token=app.config["API_KEY"],
                )
                flash("Questionnaire deleted!", "success")
                return redirect(url_for("apt_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("apt_all"))
        data["isestimated"] = (
            "<div style='color: red'>Estimated</div>"
            if data["isestimated"] == "1"
            else "<div style='color: green'>Calculated</div>"
        )
        return render_template(
            "que.html",
            ppt_id=ppt_id,
            que_id=que_id,
            data=data,
        )

    @app.route(
        "/participants/<string:ppt_id>/questionnaires/questionnaire_new",
        methods=["GET", "POST"],
    )
    @conf.token_required
    def que_new(ppt_id: str):
        """New langage questionnaire page"""
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        if request.method == "POST":
            finput = request.form
            date_now = datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M"
            )
            data = {
                "record_id": ppt_id,
                "redcap_repeat_instance": "new",
                "redcap_repeat_instrument": "language",
                "language_date_created": date_now,
                "language_date_updated": date_now,
                "language_isestimated": (
                    "1" if "inputIsEstimated" in finput.keys() else "0"
                ),
                "language_lang1": (
                    finput["inputLang1"] if "inputLang1" in finput.keys() else "0"
                ),
                "language_lang1_exp": finput["inputLang1Exp"],
                "language_lang2": (
                    finput["inputLang2"] if "inputLang2" in finput.keys() else "0"
                ),
                "language_lang2_exp": finput["inputLang2Exp"],
                "language_lang3": (
                    finput["inputLang3"] if "inputLang3" in finput.keys() else "0"
                ),
                "language_lang3_exp": finput["inputLang3Exp"],
                "language_lang4": (
                    finput["inputLang4"] if "inputLang4" in finput.keys() else "0"
                ),
                "language_lang4_exp": finput["inputLang4Exp"],
                "language_comments": finput["inputComments"],
                "language_complete": "2",
            }
            api.add_questionnaire(
                data,
                token=app.config["API_KEY"],
            )
            try:
                flash("Questionnaire added!", "success")
                return redirect(url_for("que_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("que_all"))
        return render_template("que_new.html", ppt_id=ppt_id, data_dict=data_dict)

    @app.route(
        "/participants/<string:ppt_id>/questionnaires/<string:que_id>/questionnaire_modify",
        methods=["GET", "POST"],
    )
    @conf.token_required
    def que_modify(
        que_id: str,
        ppt_id: str,
    ):
        """Modify language questionnaire page"""
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        data = (
            api.Records(token=app.config["API_KEY"]).questionnaires.records[que_id].data
        )
        for k, v in data.items():
            if "exp" in k:
                data[k] = str(round(v, None))
        if request.method == "POST":
            finput = request.form
            date_now = datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M"
            )
            data = {
                "record_id": ppt_id,
                "redcap_repeat_instance": que_id.split(":")[1],
                "language_isestimated": (
                    "1" if "inputIsEstimated" in finput.keys() else "0"
                ),
                "redcap_repeat_instrument": "language",
                "language_date_updated": date_now,
                "language_lang1": finput["inputLang1"],
                "language_lang1_exp": finput["inputLang1Exp"],
                "language_lang2": finput["inputLang2"],
                "language_lang2_exp": finput["inputLang2Exp"],
                "language_lang3": finput["inputLang3"],
                "language_lang3_exp": finput["inputLang3Exp"],
                "language_lang4": finput["inputLang4"],
                "language_lang4_exp": finput["inputLang4Exp"],
                "language_comments": finput["inputComments"],
                "language_complete": "2",
            }
            try:
                api.add_questionnaire(
                    data,
                    token=app.config["API_KEY"],
                )
                flash("Questionnaire modified!", "success")
                return redirect(url_for("que_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return render_template("que_all.html", ppt_id=ppt_id)
        return render_template(
            "que_modify.html",
            ppt_id=ppt_id,
            que_id=que_id,
            data=data,
            data_dict=data_dict,
        )
