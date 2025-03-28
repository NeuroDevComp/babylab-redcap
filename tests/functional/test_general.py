"""Test app genenal pages."""

from babylab.src import api
from babylab.app import create_app
from babylab.app import config as conf


def test_index_page():
    """Test index page."""
    app = create_app(env="prod")
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert app.config["API_KEY"] == "BADTOKEN"
        assert b"babylab-redcap" in response.data
        assert b"This app provides an interface to the" in response.data


def test_index_page_token():
    """Test index page."""
    app = create_app(env="prod")
    with app.test_client() as client:
        response = client.post("/", data={"apiToken": conf.get_api_key()})
        assert response.status_code == 200
        assert b"babylab-redcap" in response.data
        assert b"Incorrect token" not in response.data
        assert isinstance(app.config["RECORDS"], api.Records)

    with app.test_client() as client:
        response = client.post("/", data={"apiToken": "badtoken"})
        assert response.status_code == 200
        assert b"Incorrect token" in response.data


def test_dashboard_page(client):
    """Test index page."""
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_studies(client):
    """Test studies endpoint."""
    response = client.get("/studies")
    assert response.status_code == 200


def test_studies_input(client):
    """Test studies endpoint with input."""
    with client as c:
        response = c.post("/studies", data={"inputStudy": "1"})
        assert response.status_code == 200

    with client as c:
        response = c.post("/studies", data={"inputStudy": "2"})
        assert response.status_code == 200

    with client as c:
        response = c.post("/studies", data={"inputStudy": "3"})
        assert response.status_code == 200


def test_calendar(client):
    """Test calendar endpoint."""
    response = client.get("/calendar")
    assert response.status_code == 200


def test_other_backup(client):
    """Test backup endpoint."""
    response = client.post("/other")
    assert response.status_code == 200


def test_other(client):
    """Test other endpoint."""
    response = client.get("/other")
    assert response.status_code == 200
