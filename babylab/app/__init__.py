"""Initialize app."""

import os
import datetime
from flask import Flask
from babylab.app.routes import appointments, general, participants, questionnaires
from babylab.app import config


def create_app(env: str = "prod"):
    """Create Flask app instance."""
    if env not in ["dev", "prod", "test"]:
        raise ValueError("`env` must be one of 'dev', 'prod', 'test'")

    app = Flask(__name__, template_folder="templates")
    # load initial settings
    app.config.from_object(config.configs[env])
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = datetime.timedelta(minutes=10)
    app.config["API_KEY"] = config.configs[env].api_key
    app.config["TESTING"] = config.configs[env].testing
    app.config["RECORDS"] = None

    # import routes
    participants.ppt_routes(app)
    appointments.apt_routes(app)
    questionnaires.que_routes(app)
    general.general_routes(app)

    return app
