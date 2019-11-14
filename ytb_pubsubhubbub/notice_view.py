import re

from flask.views import MethodView
from flask import request


class YouTubeNoticeView(MethodView):

    intent_validator = lambda *args: True
    subscription_handler = None
    notice_handler = None
    """
    Expected function signature
    intent_validator(channel_id: str, mode: get_intent_mode) -> bool
    """

    @classmethod
    def set_handler(
        cls, intent_validator=None, subscription_handler=None, notice_handler=None
    ):
        cls.intent_validator = intent_validator
        cls.subscription_handler = subscription_handler
        cls.notice_handler = notice_handler

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

        def get_lease_seconds():
            return int(request.args["hub.lease_seconds"])

        def confirm_intention():
            challenge = request.args["hub.challenge"]
            return challenge, 200

        def reject_intention():
            return "", 400

        if self.intent_validator(
            channel_id=extract_channel_id(), mode=get_intent_mode()
        ):
            self.subscription_handler(
                channel_id=extract_channel_id(),
                mode=get_intent_mode(),
                lease_seconds=get_lease_seconds(),
            )

            return confirm_intention()

        return reject_intention()

    def post(self):
        self.notice_handler(request.data.decode("utf-8"))

        def response_with_success():
            return "", 200

        return response_with_success()
