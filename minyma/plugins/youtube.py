import os
from yt_dlp import YoutubeDL
import xml.etree.ElementTree as ET
from minyma.plugin import MinymaPlugin

class YouTubePlugin(MinymaPlugin):
    """Transcribe YouTube Video"""

    def __init__(self, config):
        self.config = config
        self.name = "youtube"
        self.functions = [self.transcribe_youtube]


    def transcribe_youtube(self, youtube_video_id: str):
        URLS = [youtube_video_id]

        vid = YoutubeDL({
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "ttml",
            "outtmpl": "transcript"
        })

        vid.download(URLS)
        content = self.convert_ttml_to_plain_text("transcript.en.ttml")
        os.remove("transcript.en.ttml")

        return {
            "content": content,
            "metadata": URLS,
            "error": "TTML Conversion Error" if content is None else None
        }


    def convert_ttml_to_plain_text(self, ttml_file_path):
        try:
            # Parse the TTML file
            tree = ET.parse(ttml_file_path)
            root = tree.getroot()

            # Process Text
            plain_text = ""
            for elem in root.iter():
                if elem.text:
                    plain_text += elem.text + " "

            return plain_text.strip()
        except ET.ParseError as e:
            print("[YouTubePlugin] TTML Conversion Error:", e)
            return None
