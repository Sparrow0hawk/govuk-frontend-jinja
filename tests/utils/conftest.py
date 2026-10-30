import pytest
from flask import Flask
from flask.testing import FlaskClient

from tests.utils.app import app


@pytest.fixture(name="app")
def app_fixture() -> Flask:
    return app


@pytest.fixture(name="client")
def client_fixture() -> FlaskClient:
    return app.test_client()
