from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
from dotenv import load_dotenv
import os


class Slack:
    def __init__(self):
        load_dotenv()
        self.message_template = {
            "info": {
                "emoji": ":large_blue_circle:",
                "header": "Info",
            },
            "danger": {
                "emoji": ":red_circle:",
                "header": "Error",
            }
        }

        self.channel = 'C011C9E9RC7'
        self.client = WebClient(
            token=os.environ["SLACK_BOT_TOKEN"])
        self.last_ts = None

    def post(self, message, mtype):
        blocks = self.generate_blocks(message, mtype)
        response = self.client.chat_postMessage(
            channel=self.channel, blocks=blocks)
        self.set_ts(response)

    def update(self, message, mtype):
        blocks = self.generate_blocks(message, mtype)
        response = self.client.chat_update(
            channel=self.channel,
            ts=self.last_ts,
            blocks=blocks
        )
        self.set_ts(response)

    def set_ts(self, resp):
        self.last_ts = resp['ts']

    def generate_blocks(self, message, mtype):
        blocks = []
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{self.message_template[mtype]['emoji']}*{self.message_template[mtype]['header']}*: {message}"
                }
            }
        )
        return blocks


if __name__ == "__main__":
    slack = Slack()
    slack.post('test', 'info')
