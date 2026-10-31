from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def test_tabs(client: FlaskClient, tabs_fixtures: list[dict[str, str]]) -> None:
    tabs_simple = tabs_fixtures[0]

    response = client.post("/component/tabs", json={"macro_name": "Tabs", "params": tabs_simple["options"]})

    jinja_html = BeautifulSoup(response.text, "html.parser").prettify()
    expected_html = BeautifulSoup(tabs_simple["html"], "html.parser").prettify()
    assert jinja_html == expected_html
