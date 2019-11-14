from unittest.mock import MagicMock

from flask import Flask
import pytest

from ytb_pubsubhubbub.notice_view import YouTubeNoticeView


@pytest.fixture
def client():
    app = Flask(__name__)
    app.add_url_rule("/notice", view_func=YouTubeNoticeView.as_view("notice_view"))

    class TestClient:
        def __init__(self):
            self._client = app.test_client()

        def simulate_intent_verification(self):
            """
            Spec of Intent Verification refers to
            http://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html#verifysub
            """
            return self._client.get(
                "/notice",
                query_string={
                    "hub.mode": "subscribe",
                    "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=channel_id",
                    "hub.challenge": "1234",
                    "hub.lease_seconds": 123,
                },
            )

        def simulate_content_distribution(self):
            """
            Spec of Content Distribution refers to
            http://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html#contentdistribution

            NOTE: the Link header is not simulated here
            """
            return self._client.post("/notice", data="content")

    return TestClient()


def simulate_intent_verification(client):

    return client.get(
        "/notice",
        query_string={
            "hub.mode": "subscribe",
            "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=channel_id",
            "hub.challenge": "1234",
            "hub.lease_seconds": 123,
        },
    )


def test_intent_verification(client):

    intent_validator = MagicMock(return_value=True)
    subscription_handler = MagicMock()
    YouTubeNoticeView.set_handler(
        intent_validator=intent_validator, subscription_handler=subscription_handler
    )

    resp = client.simulate_intent_verification()

    intent_validator.assert_called_with(channel_id="channel_id", mode="subscribe")
    subscription_handler.assert_called_with(
        channel_id="channel_id", mode="subscribe", lease_seconds=123
    )

    def assert_intent_confirmed():
        assert resp.status_code == 200
        assert resp.data == b"1234"

    assert_intent_confirmed()


def test_intent_verification_rejected(client):

    intent_validator = MagicMock(return_value=False)
    subscription_handler = MagicMock()
    YouTubeNoticeView.set_handler(
        intent_validator=intent_validator, subscription_handler=subscription_handler
    )

    resp = client.simulate_intent_verification()

    intent_validator.assert_called_with(channel_id="channel_id", mode="subscribe")
    subscription_handler.assert_not_called()

    def assert_intent_rejected():
        assert resp.status_code == 400

    assert_intent_rejected()


def test_content_distribution(client):
    notice_handler = MagicMock()

    YouTubeNoticeView.set_handler(notice_handler=notice_handler)

    resp = client.simulate_content_distribution()
    notice_handler.assert_called_once_with("content")

    assert resp.status_code == 200
