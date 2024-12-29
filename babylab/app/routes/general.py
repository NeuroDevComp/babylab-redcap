"""Genera routes."""

import os
from functools import wraps
import datetime
import requests
from flask import redirect, flash, render_template, url_for, request, send_file
from babylab.src import api, utils


def general_routes(app):
    """General routes."""

    def token_required(f):
        """Require login"""

        @wraps(f)
        def decorated(*args, **kwargs):
            redcap_version = api.get_redcap_version(token=app.config["API_KEY"])
            if redcap_version:
                return f(*args, **kwargs)
            flash("Access restricted. Please, log in.", "error")
            return redirect(url_for("index", redcap_version=redcap_version))

        return decorated

    @app.errorhandler(404)
    def error_404(error):
        """Error 404 page."""
        return render_template("404.html", error=error), 404

    @app.errorhandler(requests.exceptions.ReadTimeout)
    def error_443(error):
        """Error 403 page."""
        return render_template("443.html", error=error), 443

    @app.route("/", methods=["GET", "POST"])
    def index():
        """Index page"""
        redcap_version = api.get_redcap_version(token=app.config["API_KEY"])
        if request.method == "POST":
            finput = request.form
            app.config["API_KEY"] = finput["apiToken"]
            app.config["EMAIL"] = finput["email"]
            try:
                redcap_version = api.get_redcap_version(token=app.config["API_KEY"])
                if redcap_version:
                    flash("Logged in.", "success")
                    return render_template("index.html", redcap_version=redcap_version)
                flash("Incorrect token", "error")
            except ValueError as e:
                flash(f"Incorrect token: {e}", "error")
        return render_template("index.html", redcap_version=redcap_version)

    @app.route("/dashboard")
    @token_required
    def dashboard():
        """Dashboard page"""
        redcap_version = api.get_redcap_version(token=app.config["API_KEY"])
        try:
            records = api.Records(token=app.config["API_KEY"])
        except Exception:  # pylint: disable=broad-exception-caught
            return render_template("index.html", redcap_version=redcap_version)
        data_dict = api.get_data_dict(token=app.config["API_KEY"])
        data = utils.prepare_dashboard(records, data_dict)
        return render_template("dashboard.html", data=data)

    @app.route("/studies", methods=["GET", "POST"])
    @token_required
    def studies(
        selected_study: str = None,
        data: dict = None,
    ):
        """Studies page"""
        data_dict = api.get_data_dict(token=app.config["API_KEY"])

        if request.method == "POST":
            finput = request.form
            selected_study = finput["inputStudy"]
            redcap_version = api.get_redcap_version(token=app.config["API_KEY"])
            try:
                records = api.Records(token=app.config["API_KEY"])
            except Exception:  # pylint: disable=broad-exception-caught
                return redirect(url_for("index", redcap_version=redcap_version))

            data = utils.prepare_studies(
                records, data_dict=data_dict, study=selected_study
            )

            return render_template(
                "studies.html",
                data_dict=data_dict,
                selected_study=selected_study,
                data=data,
            )
        return render_template("studies.html", data_dict=data_dict, data=data)

    @app.route("/other", methods=["GET", "POST"])
    @token_required
    def other():
        """Other pages"""
        redcap_version = api.get_redcap_version(token=app.config["API_KEY"])
        try:
            records = api.Records(token=app.config["API_KEY"])
        except Exception:  # pylint: disable=broad-exception-caught
            return redirect(url_for("index", redcap_version=redcap_version))
        fname = datetime.datetime.strftime(
            datetime.datetime.now(), "backup_%Y-%m-%d-%H-%M.zip"
        )
        if request.method == "post":
            backup_file = api.redcap_backup(
                file=os.path.join("temp", fname), token=app.config["API_KEY"]
            )
            return send_file(
                backup_file,
                as_attachment=True,
            )
            # shutil.rmtree(os.path.dirname(backup_file))

        return render_template(
            "other.html",
        )

    @app.route("/download_backup", methods=["GET", "POST"])
    @token_required
    def download_backup():
        """Download backup"""
        utils.clean_tmp("tmp")
        utils.clean_tmp("../tmp")

        fname = datetime.datetime.strftime(
            datetime.datetime.now(), "backup_%Y-%m-%d-%H-%M.zip"
        )
        backup_file = api.redcap_backup(
            file=f"temp/{fname}", token=app.config["API_KEY"]
        )
        return send_file(
            "../" + backup_file,
            as_attachment=False,
        )

    @app.route("/logout", methods=["GET", "POST"])
    @token_required
    def logout():
        """Log out."""
        app.config["API_KEY"] = "BADTOKEN"
        flash("You have logged out.", category="error")
        return redirect(url_for("index"))
