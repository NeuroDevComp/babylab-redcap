"""Test participants endpoints."""

from tests import utils as tutils
from babylab.src import api


def test_ppt_all(client):
    """Test ppt_all endpoint."""
    response = client.get("/participants/")
    assert response.status_code == 200


def test_ppt(client):
    """Test ppt_all endpoint."""
    response = client.get("/participants/1")
    assert response.status_code == 200


def test_ppt_new(client):
    """Test ppt_all endpoint."""
    response = client.get("/participant_new")
    assert response.status_code == 200


def test_ppt_new_post(client, ppt_finput, token):
    """Test ppt_all endpoint."""
    ppt_id = api.get_next_id(token=token)
    assert not tutils.participant_exists(ppt_id)
    response = client.post("/participant_new", data=ppt_finput)
    assert tutils.participant_exists(ppt_id)
    assert response.status_code == 302


def test_ppt_mod(client, ppt_finput_mod):
    """Test ppt_all endpoint."""
    url = f"participants/{ppt_finput_mod['record_id']}/participant_modify"
    response = client.get(url)
    assert response.status_code == 200


def test_ppt_mod_post(client, ppt_finput_mod, token):
    """Test ppt_all endpoint."""
    ppt = api.get_participant(ppt_finput_mod["record_id"], token=token)
    url = f"/participants/{ppt_finput_mod['record_id']}/participant_modify"
    response = client.post(url, data=ppt_finput_mod)
    assert response.status_code == 302
    new_ppt = api.get_participant(ppt_finput_mod["record_id"], token=token)
    assert new_ppt.data != ppt.data
