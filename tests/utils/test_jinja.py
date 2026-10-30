import json
import tarfile
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def test_tabs(client: FlaskClient) -> None:
    npm_govuk_frontend = "https://registry.npmjs.org/govuk-frontend/6.6.0"
    response = requests.get(npm_govuk_frontend)
    dist_location = response.json()["dist"]["tarball"]
    response = requests.get(dist_location, stream=True)
    release_tar = tarfile.open(fileobj=BytesIO(response.raw.read()))
    tabs_fixture_file = release_tar.extractfile("package/dist/govuk/components/tabs/fixtures.json")
    tabs_fixture_json = json.loads(tabs_fixture_file.read())
    tabs_fixture_json["fixtures"][0]

    response = client.post(
        "/component/tabs", json={"macro_name": "Tabs", "params": tabs_fixture_json["fixtures"][0]["options"]}
    )

    jinja_html = BeautifulSoup(response.text, "html.parser").prettify()
    expected_html = BeautifulSoup(tabs_fixture_json["fixtures"][0]["html"], "html.parser").prettify()
    assert jinja_html == expected_html
