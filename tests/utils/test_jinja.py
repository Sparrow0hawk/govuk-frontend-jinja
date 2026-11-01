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
        self._npm_registry_url = "https://registry.npmjs.org/govuk-frontend/6.6.0"

    def download_package(self) -> None:
        registry_response = requests.get(self._npm_registry_url)
        registry_response.raise_for_status()
        dist_location = registry_response.json()["dist"]["tarball"]
        pkg_response = requests.get(dist_location, stream=True)
        pkg_response.raise_for_status()
        self._pkg_tarfile = tarfile.open(fileobj=BytesIO(pkg_response.raw.read()))

    def get_all_component_fixtures(self) -> list[dict[str, Any]]:
        component_fixtures_paths = [
            file.name for file in self._pkg_tarfile.getmembers() if file.name.endswith("fixtures.json")
        ]
        all_fixtures_json = [self._extract_and_read_json(file) for file in component_fixtures_paths]
        return all_fixtures_json

    def _extract_and_read_json(self, file_path: str) -> Any:
        extracted_file = self._pkg_tarfile.extractfile(file_path)
        return json.loads(extracted_file.read())


govuk_frontend_package = GovukFrontendPackage()
govuk_frontend_package.download_package()


@pytest.mark.parametrize(
    "component,options,html",
    [
        pytest.param(
            component["component"],
            fixture["options"],
            fixture["html"],
            id=f"{component["component"]}-{fixture["name"]}",
        )
        for component in govuk_frontend_package.get_all_component_fixtures()
        for fixture in component["fixtures"]
    ],
)
def test_components(client: FlaskClient, component: str, options: dict[list[dict[str, str]]], html: str) -> None:
    response = client.post(f"/component/{component}", json={"macro_name": to_title(component), "params": options})

    jinja_html = BeautifulSoup(response.text, "html.parser").prettify()
    expected_html = BeautifulSoup(html, "html.parser").prettify()
    assert jinja_html == expected_html


def to_title(text):
    if "-" in text:
        words = text.split("-")
        return "".join([word.title() for word in words])
    else:
        return text.title()
