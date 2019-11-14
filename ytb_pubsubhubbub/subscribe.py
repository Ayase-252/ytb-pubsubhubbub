import requests


def subscribe(channel_id: str, callback_url: str):
    """Send a Subscribe Request to Google hub

    
    Arguments:
        channel_id      Channel ID
        callback_url    URL of endpoint of your callback server where 
                        the notification send to
    """
    requests.post(
        "https://pubsubhubbub.appspot.com/subscribe",
        data={
            "hub.callback": callback_url,
            "hub.mode": "subscribe",
            "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id={}".format(
                channel_id
            ),
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

