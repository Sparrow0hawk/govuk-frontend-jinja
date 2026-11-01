import json
import tarfile
from io import BytesIO
from typing import Any

import pytest
import requests
from bs4 import BeautifulSoup
from flask.testing import FlaskClient


class GovukFrontendPackage:
    def __init__(self) -> None:
        self._npm_registry_url = "https://registry.npmjs.org/govuk-frontend/6.3.0"

    def download_package(self) -> None:
        registry_response = requests.get(self._npm_registry_url)
        registry_response.raise_for_status()
        dist_location = registry_response.json()["dist"]["tarball"]
        pkg_response = requests.get(dist_location, stream=True)
        pkg_response.raise_for_status()
        self._pkg_tarfile = tarfile.open(fileobj=BytesIO(pkg_response.raw.read()))

    def get_tabs_fixtures(self) -> list[dict[str, Any]]:
        fixture_json_file = self._pkg_tarfile.extractfile("package/dist/govuk/components/tabs/fixtures.json")
        fixture_json = json.loads(fixture_json_file.read())
        return fixture_json["fixtures"]


govuk_frontend_package = GovukFrontendPackage()
govuk_frontend_package.download_package()


@pytest.mark.parametrize(
    "options,html",
    [
        pytest.param(fixture["options"], fixture["html"], id=fixture["name"])
        for fixture in govuk_frontend_package.get_tabs_fixtures()
    ],
)
def test_tabs(client: FlaskClient, options: dict[list[dict[str, str]]], html: str) -> None:
    response = client.post("/component/tabs", json={"macro_name": "Tabs", "params": options})

    jinja_html = BeautifulSoup(response.text, "html.parser").prettify()
    expected_html = BeautifulSoup(html, "html.parser").prettify()
    assert jinja_html == expected_html
