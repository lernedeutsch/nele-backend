"""LEGACY local microphone listener.

This module uses the external speech_recognition/Google path and is not used by
production Flask. Production voice input uses browser SpeechRecognition or
MediaRecorder + faster-whisper.
"""

import speech_recognition as sr


class Listener:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:
            print("Mów teraz...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio, language="de-DE")
            print("Du:", text)
            return text
        except sr.UnknownValueError:
            print("Nie zrozumiałam.")
            return ""
        except sr.RequestError:
            print("Błąd połączenia z rozpoznawaniem mowy.")
            return ""
