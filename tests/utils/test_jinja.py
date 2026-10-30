import json
import tarfile
from io import BytesIO

import pytest
import requests
from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def tabs_fixtures_json() -> list[dict[str, str]]:
    npm_govuk_frontend = "https://registry.npmjs.org/govuk-frontend/6.3.0"
    response = requests.get(npm_govuk_frontend)
    dist_location = response.json()["dist"]["tarball"]
    response = requests.get(dist_location, stream=True)
    release_tar = tarfile.open(fileobj=BytesIO(response.raw.read()))
    tabs_fixture_file = release_tar.extractfile("package/dist/govuk/components/tabs/fixtures.json")
    tabs_fixture_json = json.loads(tabs_fixture_file.read())
    return tabs_fixture_json["fixtures"]


@pytest.mark.parametrize(
    "options,html",
    [pytest.param(fixture["options"], fixture["html"], id=fixture["name"]) for fixture in tabs_fixtures_json()],
)
def test_tabs(client: FlaskClient, options: dict[list[dict[str, str]]], html: str) -> None:
    response = client.post("/component/tabs", json={"macro_name": "Tabs", "params": options})

    jinja_html = BeautifulSoup(response.text, "html.parser").prettify()
    expected_html = BeautifulSoup(html, "html.parser").prettify()
    assert jinja_html == expected_html
