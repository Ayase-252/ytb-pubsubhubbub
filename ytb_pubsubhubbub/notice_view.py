import re

from flask.views import MethodView
from flask import request


class YouTubeNoticeView(MethodView):

    intent_validator = lambda *args: True
    """
    Expected function signature
    intent_validator(channel_id: str, mode: get_intent_mode) -> bool
    """

    @classmethod
    def set_handler(cls, intent_validator):
        cls.intent_validator = intent_validator

    def get(self):
        """GET method implements the intent verification of Subscriber
        on the subscriber side.
        """

        def extract_channel_id():
            topic = request.args["hub.topic"]
            channel_id_extractor = re.compile("channel_id=(?P<channel_id>.+)")
            match = channel_id_extractor.search(topic)
            return match.group("channel_id")

        def get_intent_mode():
            return request.args["hub.mode"]

        self.intent_validator(channel_id=extract_channel_id(), mode=get_intent_mode())
