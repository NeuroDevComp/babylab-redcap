"""Test API."""

import pytest
from babylab import api


def test_post_request(token):
    """Test ``post_request``."""
    assert api.post_request(
        fields={
            "content": "version",
        },
        token=token,
    ).ok


def test_redcap_version(token):
    """Test ``redcap_version``."""
    version = api.get_redcap_version(token=token)
    assert version
    assert isinstance(version, str)
    assert len(version.split(".")) == 3
    with pytest.raises(TypeError):
        api.get_redcap_version()
    with pytest.raises(TypeError):
        api.get_redcap_version(token)  # pylint: disable=too-many-function-args
    assert not api.get_redcap_version(token="wrongtoken")
    with pytest.raises(ValueError):
        api.get_redcap_version(token="bad#token")


def test_get_data_dict(token):
    """Test ``get_records``."""
    data_dict = api.get_data_dict(token=token)
    assert isinstance(data_dict, dict)
    assert all(isinstance(v, dict) for v in data_dict.values())
    with pytest.raises(TypeError):
        api.get_data_dict()


def test_get_records(token):
    """Test ``get_records``."""
    records = api.get_records(token=token)
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)
    with pytest.raises(TypeError):
        api.get_records()


def test_add_participant(participant_data, token):
    """Test ``add_participant``."""
    api.add_participant(participant_data, modifying=False, token=token)
    with pytest.raises(TypeError):
        api.add_participant(participant_data)


def test_redcap_backup(token) -> dict:
    """Test ``redcap_backup``."""
    api.redcap_backup(token=token)
    with pytest.raises(TypeError):
        api.redcap_backup()
