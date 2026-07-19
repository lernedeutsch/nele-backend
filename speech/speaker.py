import math
import os
import subprocess
import tempfile
import threading
import time
import urllib.request
import wave

from array import array
from pathlib import Path


try:
    import winsound
except ImportError:
    winsound = None


class Speaker:
    """
    Obsługa głosu Nele przy użyciu Piper.

    Metoda create_wav():
    tworzy plik WAV dla endpointu /tts.

    Metoda speak():
    tworzy i odtwarza wypowiedź lokalnie na komputerze Windows.
    """

    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent

        default_piper_windows = (
            project_root / "piper" / "piper.exe"
        )

        default_piper_linux = (
            project_root / "piper" / "piper"
        )

        default_model = (
            project_root
            / "piper"
            / "de_DE-kerstin-low.onnx"
        )

        configured_piper = os.environ.get(
            "PIPER_PATH"
        )

        configured_model = os.environ.get(
            "PIPER_MODEL_PATH"
        )

        if configured_piper:
            self.piper = configured_piper
        elif os.name == "nt":
            self.piper = str(
                default_piper_windows
            )
        else:
            self.piper = str(
                default_piper_linux
            )

        if configured_model:
            self.model = configured_model
        else:
            self.model = str(
                default_model
            )

        self.avatar_url = os.environ.get(
            "AVATAR_SERVER_URL",
            "http://127.0.0.1:5000"
        ).rstrip("/")

        print(
            f"System operacyjny: {os.name}"
        )

        print(
            f"Piper path: {self.piper}"
        )

        print(
            f"Model path: {self.model}"
        )

    def send_mouth(self, value):
        """
        Wysyła poziom otwarcia ust do serwera animacji.

        Brak serwera animacji nie zatrzymuje głosu.
        """

        try:
            value = max(
                0.0,
                min(
                    1.0,
                    float(value)
                )
            )

            urllib.request.urlopen(
                (
                    f"{self.avatar_url}"
                    f"/mouth?value={value}"
                ),
                timeout=0.2
            )

        except Exception:
            pass

    @staticmethod
    def calculate_rms(data, sample_width):
        """
        Oblicza głośność fragmentu WAV
        bez biblioteki audioop.
        """

        if not data:
            return 0.0

        if sample_width == 1:
            samples = array("B", data)

            normalized_samples = [
                sample - 128
                for sample in samples
            ]

        elif sample_width == 2:
            samples = array("h")
            samples.frombytes(data)

            if os.sys.byteorder != "little":
                samples.byteswap()

            normalized_samples = samples

        elif sample_width == 4:
            samples = array("i")
            samples.frombytes(data)

            if os.sys.byteorder != "little":
                samples.byteswap()

            normalized_samples = samples

        else:
            return 0.0

        if not normalized_samples:
            return 0.0

        square_sum = sum(
            float(sample) * float(sample)
            for sample in normalized_samples
        )

        return math.sqrt(
            square_sum
            / len(normalized_samples)
        )

    def animate_mouth_from_wav(
        self,
        wav_file
    ):
        """
        Analizuje głośność pliku WAV
        i porusza ustami Nele.
        """

        try:
            with wave.open(
                str(wav_file),
                "rb"
            ) as wav:
                sample_rate = (
                    wav.getframerate()
                )

                sample_width = (
                    wav.getsampwidth()
                )

                frames_per_chunk = max(
                    1,
                    int(
                        sample_rate * 0.05
                    )
                )

                if sample_width == 1:
                    maximum_level = 128.0

                elif sample_width == 2:
                    maximum_level = 32768.0

                elif sample_width == 4:
                    maximum_level = (
                        2147483648.0
                    )

                else:
                    maximum_level = 32768.0

                while True:
                    data = wav.readframes(
                        frames_per_chunk
                    )

                    if not data:
                        break

                    rms = self.calculate_rms(
                        data,
                        sample_width
                    )

                    normalized = (
                        rms / maximum_level
                    )

                    mouth = min(
                        1.0,
                        normalized * 12.0
                    )

                    self.send_mouth(mouth)

                    time.sleep(0.05)

        except Exception as error:
            print(
                f"Mouth animation error: "
                f"{error}"
            )

        finally:
            self.send_mouth(0.0)

    def validate_piper_files(self):
        """
        Sprawdza, czy Piper i model
        niemieckiego głosu istnieją.
        """

        piper_path = Path(self.piper)
        model_path = Path(self.model)

        print(
            f"Sprawdzam Piper: "
            f"{piper_path}"
        )

        print(
            f"Piper istnieje: "
            f"{piper_path.is_file()}"
        )

        print(
            f"Sprawdzam model: "
            f"{model_path}"
        )

        print(
            f"Model istnieje: "
            f"{model_path.is_file()}"
        )

        if not piper_path.is_file():
            raise FileNotFoundError(
                "Piper executable was not found: "
                f"{self.piper}"
            )

        if not model_path.is_file():
            raise FileNotFoundError(
                "Piper voice model was not found: "
                f"{self.model}"
            )

        if os.name != "nt":
            if not os.access(
                piper_path,
                os.X_OK
            ):
                raise PermissionError(
                    "Piper exists, but it is not "
                    "executable on Linux: "
                    f"{self.piper}"
                )

    def create_wav(
        self,
        text,
        output_file
    ):
        """
        Tworzy plik WAV z wypowiedzią Nele.

        Nie odtwarza dźwięku
        i nie usuwa pliku.

        Metoda jest przeznaczona
        dla endpointu /tts.
        """

        text = str(text).strip()

        if not text:
            raise ValueError(
                "Text for speech cannot be empty."
            )

        self.validate_piper_files()

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        command = [
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
            str(output_path),
        ]

        print(
            "Uruchamiam Piper:"
        )

        print(command)

        result = subprocess.run(
            command,
            input=text,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False
        )

        if result.stdout:
            print(
                "Piper stdout:"
            )

            print(result.stdout)

        if result.stderr:
            print(
                "Piper stderr:"
            )

            print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                "Piper zakończył pracę "
                f"z kodem {result.returncode}. "
                f"Błąd: {result.stderr}"
            )

        if not output_path.is_file():
            raise RuntimeError(
                "Piper did not create "
                "the WAV file."
            )

        if output_path.stat().st_size == 0:
            raise RuntimeError(
                "Piper created an empty "
                "WAV file."
            )

        return str(output_path)

    def speak(self, text):
        """
        Tworzy wypowiedź i odtwarza ją lokalnie.

        Lokalne odtwarzanie jest dostępne
        na Windowsie.

        Endpoint /tts korzysta z create_wav(),
        a nie z speak().
        """

        text = str(text).strip()

        if not text:
            return

        print(
            "Nele:",
            text
        )

        temporary_file = (
            tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            )
        )

        wav_file = temporary_file.name

        temporary_file.close()

        try:
            self.create_wav(
                text,
                wav_file
            )

            mouth_thread = (
                threading.Thread(
                    target=(
                        self.animate_mouth_from_wav
                    ),
                    args=(wav_file,),
                    daemon=True
                )
            )

            mouth_thread.start()

            if winsound is None:
                raise RuntimeError(
                    "Local audio playback is "
                    "available only on Windows. "
                    "Use create_wav() "
                    "on the server."
                )

            winsound.PlaySound(
                wav_file,
                winsound.SND_FILENAME
            )

            mouth_thread.join()

            self.send_mouth(0.0)

        except Exception as error:
            print(
                f"Speech error: {error}"
            )

            self.send_mouth(0.0)

            raise

        finally:
            self.send_mouth(0.0)

            if os.path.exists(
                wav_file
            ):
                try:
                    os.remove(
                        wav_file
                    )

                except OSError:
                    pass
