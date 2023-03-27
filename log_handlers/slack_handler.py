""" A logging handler that sends messages to Slack. """
from logging import Handler, LogRecord
from slack_sdk import WebClient


class SlackHandler(Handler):
    """ A logging handler that sends messages to Slack.

        Any keys supported by the API are allowed: https://api.slack.com/methods/chat.postMessage
        The only required key is 'channel'.

        Args:
            token (str): The Slack API token.
            channel (str): The channel to send messages to.
            username (str, optional): The username to send messages as.
            icon_emoji (str, optional): The emoji to use as the icon.

        Example usage:
            .. code-block:: python

                import os
                from loguru import logger
                from log_handlers import SlackHandler

                # Create a SlackHandler and add it to the logger
                token = os.getenv('SLACK_TOKEN')
                channel = os.getenv('SLACK_CHANNEL')
                username = os.getenv('SLACK_USERNAME')
                icon_emoji = os.getenv('SLACK_ICON_EMOJI')

                slack_handler = SlackHandler(token=token, channel=channel, \
username=username, icon_emoji=icon_emoji)
                logger.add(slack_handler, level="DEBUG", backtrace=False, diagnose=False)
            ::
    """
    def __init__(self, token: str, channel: str, username: str, icon_emoji: str):
        """ Initialize the handler."""
        super().__init__()
        self.slack_client = WebClient(token)
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji

    def emit(self, record: LogRecord):
        # formatting is based on the provided Formatter when the handler is created
        msg = self.format(record)
        # no error handling; if there is an issue, slack.errors.SlackApiError will be raised
        # as_user must be False in order to set custom username and icon
        self.slack_client.chat_postMessage(channel=self.channel, text=msg, \
            username=self.username, icon_emoji=self.icon_emoji)

    def send_message(self, msg: str):
        """Send a message

        For testing simple messaging without having to create a LogRecord.

        Args:
            msg (str): The message to send
        """
        self.slack_client.chat_postMessage(channel=self.channel, text=msg, \
            username=self.username, icon_emoji=self.icon_emoji)
