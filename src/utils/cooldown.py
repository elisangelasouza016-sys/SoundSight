import time
from dataclasses import dataclass, field

@dataclass
class AudioCooldown:
    seconds: float = 5.0
    _last_text: str = ""
    _last_time: float = field(default_factory=lambda: 0.0)

    def can_speak(self, text: str) -> bool:
        now = time.time()
        if not text:
            return False
        if text != self._last_text:
            self._last_text = text
            self._last_time = now
            return True
        if now - self._last_time >= self.seconds:
            self._last_time = now
            return True
        return False
