import os
import tempfile
from gtts import gTTS


class TTSService:
    def __init__(self, lang="pt-br"):
        self.lang = lang

    def text_to_audio_file(self, text: str) -> str:
        if not text:
            return ""

        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, "soundsight_audio.mp3")

        tts = gTTS(text=text, lang=self.lang)
        tts.save(audio_path)

        return audio_path
