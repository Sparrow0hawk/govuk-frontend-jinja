import json
import tarfile
from io import BytesIO

import pytest
import requests
from flask import Flask
from flask.testing import FlaskClient

from tests.utils.app import app


@pytest.fixture(name="app")
def app_fixture() -> Flask:
    return app


@pytest.fixture(name="client")
def client_fixture() -> FlaskClient:
    return app.test_client()


@pytest.fixture(name="tabs_fixtures")
def tabs_fixtures_fixture() -> list[dict[str, str]]:
    npm_govuk_frontend = "https://registry.npmjs.org/govuk-frontend/6.6.0"
    response = requests.get(npm_govuk_frontend)
    dist_location = response.json()["dist"]["tarball"]
    response = requests.get(dist_location, stream=True)
    release_tar = tarfile.open(fileobj=BytesIO(response.raw.read()))
    tabs_fixture_file = release_tar.extractfile("package/dist/govuk/components/tabs/fixtures.json")
    tabs_fixture_json = json.loads(tabs_fixture_file.read())
    return tabs_fixture_json["fixtures"]
