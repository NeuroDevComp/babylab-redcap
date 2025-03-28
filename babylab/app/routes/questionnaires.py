"""Questionnaires routes."""

from datetime import datetime
import requests
from flask import flash, redirect, render_template, url_for, request
from babylab.src import api, utils
from babylab.app import config as conf


def prepare_que(records: api.Records, data_dict: dict):
    """Prepare questionnaires page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = utils.get_que_table(records, data_dict=data_dict)
    classes = "table table-hover"
    df["modify_button"] = [
        utils.fmt_modify_button(que_id=q) for q in df["questionnaire_id"]
    ]
    df["questionnaire_id"] = [utils.fmt_que_id(q) for q in df["questionnaire_id"]]
    df["record_id"] = [utils.fmt_ppt_id(i) for i in df.index]
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
            "date_updated": "Updated",
            "date_created": "Created",
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
        classes=f'{classes}" id = "quetable',
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )
    return {"table": table}


def que_routes(app):
    """Questionnaire routes."""

    @app.route("/questionnaires/")
    @conf.token_required
    def que_all():
        """Participants database"""
        records = app.config["RECORDS"]
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        data = prepare_que(records, data_dict=data_dict)
        return render_template(
            "que_all.html",
            data=data,
            data_dict=data_dict,
            n_que=len(records.questionnaires.records),
        )

    @app.route("/questionnaires/<string:que_id>", methods=["GET", "POST"])
    @conf.token_required
    def que(que_id: str):
        """Show a language questionnaire"""
        token = app.config["API_KEY"]
        data_dict = api.get_data_dict(token=token)
        ppt_id, repeat_id = que_id.split(":")
        ppt = api.get_participant(ppt_id, token=token)
        que = ppt.questionnaires.records[que_id]
        data = utils.replace_labels(que.data, data_dict)
        if request.method == "POST":
            try:
                api.delete_questionnaire(
                    data={"record_id": ppt_id, "redcap_repeat_instance": repeat_id},
                    token=token,
                )
                flash("Questionnaire deleted!", "success")
                return redirect(url_for("que_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("que_all"))
        data["isestimated"] = (
            "<div style='color: red'>Estimated</div>"
            if data["isestimated"] == "1"
            else "<div style='color: green'>Calculated</div>"
        )
        return render_template("que.html", ppt_id=ppt_id, que_id=que_id, data=data)

    @app.route("/questionnaires/questionnaire_new", methods=["GET", "POST"])
    @conf.token_required
    def que_new(ppt_id: str = None):
        """New langage questionnaire page"""
        if ppt_id is None:
            ppt_id = request.args.get("ppt_id")
        token = app.config["API_KEY"]
        data_dict = api.get_data_dict(token=token)
        if request.method == "POST":
            finput = request.form
            date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            data = {
                "record_id": ppt_id,
                "redcap_repeat_instance": "new",
                "redcap_repeat_instrument": "language",
                "language_date_created": date_now,
                "language_date_updated": date_now,
                "language_isestimated": ("1" if "inputIsEstimated" in finput else "0"),
                "language_lang1": (
                    finput["inputLang1"] if "inputLang1" in finput else "0"
                ),
                "language_lang1_exp": finput["inputLang1Exp"],
                "language_lang2": (
                    finput["inputLang2"] if "inputLang2" in finput else "0"
                ),
                "language_lang2_exp": finput["inputLang2Exp"],
                "language_lang3": (
                    finput["inputLang3"] if "inputLang3" in finput else "0"
                ),
                "language_lang3_exp": finput["inputLang3Exp"],
                "language_lang4": (
                    finput["inputLang4"] if "inputLang4" in finput else "0"
                ),
                "language_lang4_exp": finput["inputLang4Exp"],
                "language_comments": finput["inputComments"],
                "language_complete": "2",
            }
            try:
                api.add_questionnaire(data, token=token)
                records = conf.get_records_or_index(token=token)
                app.config["RECORDS"] = records
                flash(f"Questionnaire added! ({ppt_id})", "success")
                return redirect(url_for("que_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("que_all"))
        return render_template("que_new.html", ppt_id=ppt_id, data_dict=data_dict)

    @app.route(
        "/questionnaires/<string:que_id>/questionnaire_modify", methods=["GET", "POST"]
    )
    @conf.token_required
    def que_modify(
        que_id: str, ppt_id: str = None, data: dict = None, data_dict: dict = None
    ):
        """Modify language questionnaire page"""
        token = app.config["API_KEY"]
        if data_dict is None:
            data_dict = api.get_data_dict(token=token)
        ppt_id, repeat_id = que_id.split(":")
        ppt = api.get_participant(ppt_id, token=token)
        data = ppt.questionnaires.records[que_id].data
        data = utils.replace_labels(data, data_dict)
        if request.method == "POST":
            finput = request.form
            date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            data = {
                "record_id": ppt_id,
                "redcap_repeat_instance": repeat_id,
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
                api.add_questionnaire(data, token=token)
                records = conf.get_records_or_index(token=token)
                app.config["RECORDS"] = records
                flash("Questionnaire modified!", "success")
                return redirect(url_for("que_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return render_template(
                    "que_all.html", ppt_id=ppt_id, data_dict=data_dict
                )
        return render_template(
            "que_modify.html",
            que_id=que_id,
            data=data,
            data_dict=data_dict,
            ppt_id=ppt_id,
        )
