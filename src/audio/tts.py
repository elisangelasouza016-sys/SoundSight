import os
import tempfile
from pathlib import Path
from typing import Iterable

class TTSService:
    """Gera feedback sonoro simples.

    Preferência: gTTS porque funciona melhor em apps Streamlit hospedados.
    Fallback: pyttsx3 para execução local/offline.
    """

    def build_sentence(self, labels_pt: Iterable[str]) -> str:
        labels = list(dict.fromkeys([x for x in labels_pt if x]))
        if not labels:
            return "Nenhum objeto identificado com segurança."
        if len(labels) == 1:
            return f"Estou vendo {self._article(labels[0])} {labels[0]}."
        if len(labels) == 2:
            joined = f"{self._article(labels[0])} {labels[0]} e {self._article(labels[1])} {labels[1]}"
        else:
            first = ", ".join(f"{self._article(x)} {x}" for x in labels[:-1])
            joined = f"{first} e {self._article(labels[-1])} {labels[-1]}"
        return f"Estou vendo {joined}."

    def save_to_file(self, text: str, filename: str | None = None) -> str | None:
        filename = filename or "soundsight_audio.mp3"
        output_path = Path(tempfile.gettempdir()) / filename
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang="pt-br")
            tts.save(str(output_path))
            return str(output_path)
        except Exception:
            pass
        try:
            import pyttsx3
            wav_path = output_path.with_suffix(".wav")
            engine = pyttsx3.init()
            engine.save_to_file(text, str(wav_path))
            engine.runAndWait()
            return str(wav_path) if os.path.exists(wav_path) else None
        except Exception:
            return None

    @staticmethod
    def _article(label: str) -> str:
        feminine_endings = ("a", "ão")
        exceptions_masc = {"sofá", "vaso", "garfo", "livro", "celular", "notebook", "controle remoto"}
        if label in exceptions_masc:
            return "um"
        return "uma" if label.endswith(feminine_endings) else "um"
