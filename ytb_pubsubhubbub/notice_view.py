import re

from flask.views import MethodView
from flask import request


class IntentValidationHandler:
    def __init__(
        self, subscription_handler, intent_validator=(lambda channel_id, mode: True)
    ):
        """ IntentValidationHandler

        Instance used by YouTubeNoticeView to handle Intent 
        Verification process described in 
        [Pubsubhubbub Protocol](http://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html#verifysub)

        The `subscription_handler` are called when intention is confirmed,
        which can be used to update database to show the channel is subscribed
        successfully.

        `subscription_handler` is expected to have signature as `(channel_id: str, mode: str, lease_seconds: str)`
        `channel_id` is the id of channel being subscribed, and `mode` is one of values `subscribe` or `unsubscribe`
        and `lease_seconds` is the valid duration of subscription in seconds. For example, 
        `lease_seconds = 500` means the subscription will last for 500 seconds.
        After that, you will not receive content distribution from that channel.

        According to the spec of Pubsubhubbub, you takes the responsibility
        to verify whether the intention of subscription is correct, such as
        right channel and right mode (subscribe or unsubscribe). iF you 
        wanna to check the correctness of the intention. You can pass a 
        `intent_validator`. 
        
        `intent_validator` is expected to have signature as `(channel_id, mode: str)`.
        You should return a boolean value to show whether the intent passes
        check. If you return a `False`, the intent will be rejected and will
        not be handled by subscription_handler.

        `intent_validator` is optional. If `intent_validator` is not passed,
        the intention will always be accepted.
        
        Arguments:
            subscription_handler {[type]} -- [description]
        
        Keyword Arguments:
            intent_validator {[type]} -- [description] (default: {lambdachannel_id})
        """

        self.intent_validator = intent_validator
        self.subscription_handler = subscription_handler


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
        cls,
        intent_validator=None,
        subscription_handler=None,
        notice_handler=None,
        intent_validation_handler=None,
    ):
        cls.intent_validator = intent_validator
        cls.subscription_handler = subscription_handler
        cls.notice_handler = notice_handler
        cls.intent_validation_handler = intent_validation_handler

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

        if self.intent_validation_handler.intent_validator(
            channel_id=extract_channel_id(), mode=get_intent_mode()
        ):
            self.intent_validation_handler.subscription_handler(
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
