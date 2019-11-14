from unittest.mock import MagicMock

from flask import Flask

from ytb_pubsubhubbub.notice_view import YouTubeNoticeView


def test_intent_verification():
    intent_validator = MagicMock()

    YouTubeNoticeView.set_handler(intent_validator=intent_validator)

    app = Flask(__name__)
    app.add_url_rule("/notice", view_func=YouTubeNoticeView.as_view("notice_view"))

    client = app.test_client()
    client.get(
        "/notice",
        query_string={
            "hub.mode": "subscribe",
            "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=channel_id",
            "hub.challenge": "1234",
            "hub.lease_seconds": 123,
        },
    )

    intent_validator.assert_called_with(channel_id="channel_id", mode="subscribe")

