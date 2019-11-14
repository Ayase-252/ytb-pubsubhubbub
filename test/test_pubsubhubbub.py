from unittest.mock import patch

from ytb_pubsubhubbub import subscribe


@patch("requests.post")
def test_send_subscription_request(request_post):
    subscribe(channel_id="CHANNEL_ID", callback_url="http://callback/path/to/endpoint")

    request_post.assert_called_once_with(
        "https://pubsubhubbub.appspot.com/subscribe",
        data={
            "hub.callback": "http://callback/path/to/endpoint",
            "hub.mode": "subscribe",
            "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=CHANNEL_ID",
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

