import json
import urllib.parse
import requests
from minyma.plugin import MinymaPlugin


class HomeAssistantPlugin(MinymaPlugin):
    """Perform Home Assistant Command"""

    def __init__(self, config):
        self.config = config
        self.name = "home_assistant"
        self.functions = []

        if config.HOME_ASSISTANT_API_KEY and config.HOME_ASSISTANT_URL:
            self.functions = [self.home_automation_command]
        if not config.HOME_ASSISTANT_API_KEY:
            print("[HomeAssistantPlugin] Missing HOME_ASSISTANT_API_KEY")
        if not config.HOME_ASSISTANT_URL:
            print("[HomeAssistantPlugin] Missing HOME_ASSISTANT_URL")

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
            r = resp.json()
            text = r["response"]["speech"]["plain"]["speech"]

            return {
                "content": text,
                "metadata": r,
                "error": None
            }
        except requests.JSONDecodeError:
            return {
                "content": None,
                "metadata": None,
                "error": "Command Failed"
            }
