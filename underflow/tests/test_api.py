from http import HTTPStatus
from unittest.mock import patch

from assertpy import assert_that
from fastapi.testclient import TestClient

from underflow.api import app

client = TestClient(app)


def test_status():
    response = client.get("/status")
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    assert_that(response.json()).contains_key("results", "token")


@patch("underflow.api.bg_get_next_pages", return_value=None)
def test_search_with_preempt_load(preempt_mock, mocked_api):
    response = client.post("/search", json={"query": "flask"})
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    results = response.json()["results"]
    assert_that(response.json()).contains_key("results")
    assert_that(results).is_length(30)
    assert_that(preempt_mock.called).is_true()
