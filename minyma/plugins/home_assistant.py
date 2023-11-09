import json
import urllib.parse
import requests
from minyma.plugin import MinymaPlugin


class HomeAssistantPlugin(MinymaPlugin):
    """Perform Home Assistant Command"""

    def __init__(self, config):
        self.config = config
        self.name = "home_assistant"


        if not config.HOME_ASSISTANT_API_KEY or not config.HOME_ASSISTANT_URL:
            if not config.HOME_ASSISTANT_API_KEY:
                print("[HomeAssistantPlugin] Missing HOME_ASSISTANT_API_KEY")
            if not config.HOME_ASSISTANT_URL:
                print("[HomeAssistantPlugin] Missing HOME_ASSISTANT_URL")

            self.functions = []
        else:
            self.functions = [self.home_automation_command]

    def home_automation_command(self, natural_language_command: str):
        url = urllib.parse.urljoin(self.config.HOME_ASSISTANT_URL, "/api/conversation/process")
        headers = {
            "Authorization": "Bearer %s" % self.config.HOME_ASSISTANT_API_KEY,
            "Content-Type": "application/json",
        }

        data = {"text": natural_language_command, "language": "en"}
        resp = requests.post(url, json=data, headers=headers)

        # Parse JSON
        try:
            return json.dumps(resp.json())
        except requests.JSONDecodeError:
            return json.dumps({ "error": "Command Failed" })
