import logging
try:
    import speech_recognition as sr 
    import pyttsx3 
    HAS_VOICE = True
except Exception:
    HAS_VOICE = False

import threading

logger = logging.getLogger(__name__)

class VoiceEngine:
    def __init__(self):
        if not HAS_VOICE:
            raise RuntimeError("Voice libraries are not available (speech_recognition/pyttsx3).")
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 170)

    def listen(self) -> str:
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
            return self.recognizer.recognize_google(audio)
        except Exception as e:
            logger.exception("Voice listen failed: %s", e)
            return ""

    def _speak_thread(self, text: str):
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception:
            logger.exception("TTS speak failed")

    def speak(self, text: str):
        thread = threading.Thread(target=self._speak_thread, args=(text,), daemon=True)
        thread.start()
