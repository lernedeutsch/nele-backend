import os
import subprocess
import tempfile
import urllib.request
import winsound
import wave
import audioop
import time
import threading


class Speaker:

    def __init__(self):
        self.piper = "piper/piper/piper.exe"
        self.model = "piper/de_DE-kerstin-low.onnx"

    def send_mouth(self, value):
        try:
            value = max(0.0, min(1.0, float(value)))
            urllib.request.urlopen(
                f"http://127.0.0.1:5000/mouth?value={value}",
                timeout=0.2
            )
        except:
            pass

    def animate_mouth_from_wav(self, wav_file):
        try:
            with wave.open(wav_file, "rb") as wav:
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                frames_per_chunk = int(sample_rate * 0.05)

                while True:
                    data = wav.readframes(frames_per_chunk)
                    if not data:
                        break

                    rms = audioop.rms(data, sample_width)
                    mouth = min(1.0, rms / 2500)

                    self.send_mouth(mouth)
                    time.sleep(0.05)

        except:
            pass
        finally:
            self.send_mouth(0)

    def speak(self, text):
        print("Nele:", text)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav:
            wav_file = wav.name

        try:
            subprocess.run(
                [
                    self.piper,
                    "--model",
                    self.model,
                    "--length_scale",
                    "1.05",
                    "--noise_scale",
                    "0.60",
                    "--noise_w",
                    "0.80",
                    "--output_file",
                    wav_file,
                ],
                input=text,
                text=True,
                encoding="utf-8",
                check=True
            )

            mouth_thread = threading.Thread(
                target=self.animate_mouth_from_wav,
                args=(wav_file,)
            )
            mouth_thread.start()

            winsound.PlaySound(wav_file, winsound.SND_FILENAME)

            mouth_thread.join()
            self.send_mouth(0)

        finally:
            self.send_mouth(0)

            if os.path.exists(wav_file):
                os.remove(wav_file)
