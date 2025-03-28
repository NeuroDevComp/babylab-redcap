"""Appointments routes."""

from datetime import datetime
import requests
from flask import flash, redirect, render_template, url_for, request
from babylab.src import api, utils
from babylab.app import config as conf


def prepare_apt(records: api.Records, data_dict: dict = None, study: str = None):
    """Prepare record ID page.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        data_dict (dict): Data dictionary as returned by ``api.get_data_dictionary``.
        study (str, optional): Study to filter for. Defaults to None.

    Returns:
        dict: Parameters for the participants endpoint.
    """  # pylint: disable=line-too-long
    df = utils.get_apt_table(records, data_dict=data_dict, study=study)
    classes = "table table-hover table-responsive"
    df["record_id"] = [utils.fmt_ppt_id(i) for i in df.index]
    df["modify_button"] = [
        utils.fmt_modify_button(p, a) for p, a in zip(df.index, df["appointment_id"])
    ]
    df["appointment_id"] = [utils.fmt_apt_id(i) for i in df["appointment_id"]]

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
            "comments",
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
            "comments": "Comments",
            "modify_button": "",
        }
    )

    table = df.to_html(
        classes=f'{classes}" id = "apttable',
        escape=False,
        justify="left",
        index=False,
        bold_rows=True,
    )

    return {"table": table}


def apt_routes(app):
    """Appointments routes."""

    @app.route("/appointments/")
    @conf.token_required
    def apt_all():
        """Appointments database"""
        token = app.config["API_KEY"]
        records = app.config["RECORDS"]
        data_dict = api.get_data_dict(token=token)
        data = prepare_apt(records, data_dict=data_dict)
        return render_template(
            "apt_all.html",
            data=data,
            n_apt=len(records.appointments.records),
        )

    @app.route("/appointments/<string:apt_id>", methods=["GET", "POST"])
    @conf.token_required
    def apt(apt_id: str = None):
        """Show the record_id for that appointment"""
        token = app.config["API_KEY"]
        data_dict = api.get_data_dict(token=token)
        ppt_id, repeat_id = apt_id.split(":")
        ppt = api.get_participant(ppt_id, token=token)
        apt = ppt.appointments.records[apt_id]
        data = utils.replace_labels(apt.data, data_dict)

        age_created = (ppt.data["age_created_months"], ppt.data["age_created_days"])
        ts = datetime.strptime(ppt.data["date_created"], "%Y-%m-%d %H:%M:%S")
        apt_date = datetime.strptime(data["date"], "%Y-%m-%d %H:%M")
        data["age_apt_months"], data["age_apt_days"] = api.get_age(
            age_created, ts=ts, ts_new=apt_date
        )

        ppt.data = utils.replace_labels(ppt.data, data_dict)
        ppt.data["age_now_months"] = str(ppt.data["age_now_months"])
        ppt.data["age_now_days"] = str(ppt.data["age_now_days"])
        data["age_apt_months"] = str(data["age_apt_months"])
        data["age_apt_days"] = str(data["age_apt_days"])
        if request.method == "POST":
            try:
                api.delete_appointment(
                    data={"record_id": ppt_id, "redcap_repeat_instance": repeat_id},
                    token=app.config["API_KEY"],
                )
                flash("Appointment deleted!", "success")
                return redirect(url_for("apt_all"))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return redirect(url_for("apt_all"))
        return render_template(
            "apt.html",
            apt_id=apt_id,
            ppt_id=ppt_id,
            data=data,
            participant=ppt.data,
        )

    @app.route("/appointments/appointment_new", methods=["GET", "POST"])
    @conf.token_required
    def apt_new(ppt_id: str = None):
        """New appointment page"""
        if ppt_id is None:
            ppt_id = request.args.get("ppt_id")
        token = app.config["API_KEY"]
        records = app.config["RECORDS"]
        data_dict = api.get_data_dict(token=token)
        if request.method == "POST":
            finput = request.form
            date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            data = {
                "record_id": ppt_id,
                "redcap_repeat_instance": "new",
                "redcap_repeat_instrument": "appointments",
                "appointment_study": finput["inputStudy"],
                "appointment_date_created": date_now,
                "appointment_date_updated": date_now,
                "appointment_date": finput["inputDate"],
                "appointment_taxi_address": finput["inputTaxiAddress"],
                "appointment_taxi_isbooked": (
                    "1" if "inputTaxiIsbooked" in finput else "0"
                ),
                "appointment_status": finput["inputStatus"],
                "appointment_comments": finput["inputComments"],
                "appointments_complete": "2",
            }

            try:
                api.add_appointment(data, token=token)
                records = conf.get_records_or_index(token=token)
                app.config["RECORDS"] = records
                flash(f"Appointment added! ({ppt_id})", "success")
                return redirect(url_for("apt_all", records=records))
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return render_template("apt_new.html", data_dict=data_dict)

        return render_template("apt_new.html", ppt_id=ppt_id, data_dict=data_dict)

    @app.route(
        "/appointments/<string:apt_id>/appointment_modify", methods=["GET", "POST"]
    )
    @conf.token_required
    def apt_modify(apt_id: str, data: dict = None, data_dict: dict = None):
        """Modify appointment page"""
        token = app.config["API_KEY"]
        if data_dict is None:
            data_dict = api.get_data_dict(token=token)
        ppt_id, repeat_id = apt_id.split(":")
        ppt = api.get_participant(ppt_id, token=token)
        data = ppt.appointments.records[apt_id].data
        data = utils.replace_labels(data, data_dict)
        if request.method == "POST":
            finput = request.form
            date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            data = {
                "record_id": ppt_id,
                "redcap_repeat_instance": repeat_id,
                "redcap_repeat_instrument": "appointments",
                "appointment_study": finput["inputStudy"],
                "appointment_date_updated": date_now,
                "appointment_date": finput["inputDate"],
                "appointment_taxi_address": finput["inputTaxiAddress"],
                "appointment_taxi_isbooked": (
                    "1" if "inputTaxiIsbooked" in finput.keys() else "0"
                ),
                "appointment_status": finput["inputStatus"],
                "appointment_comments": finput["inputComments"],
                "appointments_complete": "2",
            }

            try:
                api.add_appointment(data, token=token)
                records = conf.get_records_or_index(token=token)
                app.config["RECORDS"] = records
                flash("Appointment modified!", "success")
                return redirect(
                    url_for(
                        "apt",
                        apt_id=apt_id,
                        ppt_id=data["record_id"],
                        data=data,
                        participant=ppt.data,
                    )
                )
            except requests.exceptions.HTTPError as e:
                flash(f"Something went wrong! {e}", "error")
                return render_template(
                    "apt_modify.html", ppt_id=ppt_id, data_dict=data_dict
                )
        return render_template(
            "apt_modify.html", apt_id=apt_id, data=data, data_dict=data_dict
        )
