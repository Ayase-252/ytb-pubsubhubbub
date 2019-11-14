from unittest.mock import MagicMock

from flask import Flask
import pytest

from ytb_pubsubhubbub.notice_view import YouTubeNoticeView, IntentValidationHandler


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


def assert_intent_confirmed(resp):
    assert resp.status_code == 200
    assert resp.data == b"1234"


def assert_intent_rejected(resp):
    assert resp.status_code == 400


def setup_intent_validation_mocker(intent_validation_result):
    intent_validator = MagicMock(return_value=intent_validation_result)
    subscription_handler = MagicMock()
    intent_validation_handler = IntentValidationHandler(
        subscription_handler=subscription_handler, intent_validator=intent_validator
    )
    YouTubeNoticeView.set_handler(intent_validation_handler=intent_validation_handler)
    return (intent_validator, subscription_handler)


def test_intent_verification(client):
    (intent_validator, subscription_handler) = setup_intent_validation_mocker(True)

    assert_intent_confirmed(client.simulate_intent_verification())
    intent_validator.assert_called_with(channel_id="channel_id", mode="subscribe")
    subscription_handler.assert_called_with(
        channel_id="channel_id", mode="subscribe", lease_seconds=123
    )


def test_intent_verification_rejected(client):
    (intent_validator, subscription_handler) = setup_intent_validation_mocker(False)

    assert_intent_rejected(client.simulate_intent_verification())
    intent_validator.assert_called_with(channel_id="channel_id", mode="subscribe")
    subscription_handler.assert_not_called()


def test_no_intent_validator_will_cause_verification_always_pass(client):
    subscription_handler = MagicMock()
    intent_validation_handler = IntentValidationHandler(
        subscription_handler=subscription_handler
    )
    YouTubeNoticeView.set_handler(intent_validation_handler=intent_validation_handler)

    assert_intent_confirmed(client.simulate_intent_verification())


def test_content_distribution(client):
    notice_handler = MagicMock()

    YouTubeNoticeView.set_handler(notice_handler=notice_handler)

    resp = client.simulate_content_distribution()
    notice_handler.assert_called_once_with("content")

    assert resp.status_code == 200
