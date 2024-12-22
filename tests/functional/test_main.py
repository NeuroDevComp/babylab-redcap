"""Test main app."""

import os
import datetime
from flask import Flask
from json import loads
from babylab import api


def create_app():
    """App initializer."""
    # Create the Flask application
    app = Flask(__name__)

    # Configure the Flask application
    app = Flask(__name__, template_folder="templates")
    app.config["API_KEY"] = "TOKEN"
    app.config["EMAIL"] = "EMAIL"
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = datetime.timedelta(minutes=10)

    return app


def test_index_page(test_client, token):
    """Test index page."""
    redcap_version = api.get_redcap_version(token=token)
    response = test_client.get("/")
    data = loads(response.get_data())
    assert len(data) > 0
