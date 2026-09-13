# ==========================================
# NELE – PRONUNCIATION AUDIO
# WHISPER ASR
# STUDENT MEMORY 2.0
# ==========================================
#
# Ten moduł będzie odpowiedzialny za:
#
# prawdziwe nagranie audio
#        ↓
# Whisper
#        ↓
# rozpoznany tekst niemiecki
#
# WAŻNE:
#
# Ten moduł NIE ocenia jeszcze wymowy.
#
# Najpierw musimy niezawodnie rozpoznać,
# co użytkownik powiedział.
#
# Dopiero później dołączymy:
#
# pronunciation_coach.py
# pronunciation_feedback.py
# pronunciation_memory.py
#
# ==========================================

import os
import threading

from pathlib import Path


# ==========================================
# USTAWIENIA WHISPER
# ==========================================

WHISPER_MODEL_NAME = (
    os.environ.get(
        "NELE_WHISPER_MODEL",
        "tiny"
    ).strip()
    or
    "tiny"
)


WHISPER_DEVICE = (
    os.environ.get(
        "NELE_WHISPER_DEVICE",
        "cpu"
    ).strip()
    or
    "cpu"
)


WHISPER_COMPUTE_TYPE = (
    os.environ.get(
        "NELE_WHISPER_COMPUTE_TYPE",
        "int8"
    ).strip()
    or
    "int8"
)


WHISPER_LANGUAGE = "de"


# ==========================================
# BEAM SIZE
# ==========================================

def get_whisper_beam_size():

    value = os.environ.get(
        "NELE_WHISPER_BEAM_SIZE",
        "5"
    )


    try:

        value = int(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        value = 5


    return max(
        1,
        min(
            value,
            10
        )
    )


# ==========================================
# VAD
# ==========================================

def get_whisper_vad_filter():

    value = str(
        os.environ.get(
            "NELE_WHISPER_VAD",
            "true"
        )
    ).strip().lower()


    return value not in {
        "0",
        "false",
        "no",
        "off"
    }


# ==========================================
# MODEL – ŁADOWANY TYLKO RAZ
# ==========================================

_whisper_model = None

_whisper_model_lock = (
    threading.Lock()
)


# ==========================================
# CZY FASTER-WHISPER JEST DOSTĘPNY
# ==========================================

def is_whisper_available():

    try:

        import faster_whisper

        return True

    except ImportError:

        return False


# ==========================================
# INFORMACJA O ASR
# ==========================================

def get_whisper_status():

    return {
        "available":
            is_whisper_available(),

        "model":
            WHISPER_MODEL_NAME,

        "device":
            WHISPER_DEVICE,

        "compute_type":
            WHISPER_COMPUTE_TYPE,

        "language":
            WHISPER_LANGUAGE,

        "beam_size":
            get_whisper_beam_size(),

        "vad_filter":
            get_whisper_vad_filter()
    }


# ==========================================
# POBRANIE MODELU
# ==========================================
#
# Model jest ładowany dopiero przy pierwszym
# prawdziwym nagraniu.
#
# Nie ładujemy go przy starcie Flask,
# ponieważ Render nie powinien zużywać
# pamięci, zanim ASR będzie potrzebne.
# ==========================================

def get_whisper_model():

    global _whisper_model


    if _whisper_model is not None:

        return _whisper_model


    with _whisper_model_lock:

        if _whisper_model is not None:

            return _whisper_model


        try:

            from faster_whisper import (
                WhisperModel
            )

        except ImportError as error:

            raise RuntimeError(
                "faster-whisper is not installed."
            ) from error


        print(
            "Nele Whisper: loading model:",
            WHISPER_MODEL_NAME
        )


        _whisper_model = WhisperModel(
            WHISPER_MODEL_NAME,
            device=WHISPER_DEVICE,
            compute_type=(
                WHISPER_COMPUTE_TYPE
            )
        )


        print(
            "Nele Whisper: model ready."
        )


        return _whisper_model


# ==========================================
# SPRAWDZENIE PLIKU AUDIO
# ==========================================

def validate_audio_file(
    audio_path
):

    if not audio_path:

        return {
            "ok": False,
            "error": "audio_path_missing"
        }


    try:

        path = Path(
            audio_path
        )

    except Exception:

        return {
            "ok": False,
            "error": "invalid_audio_path"
        }


    if not path.exists():

        return {
            "ok": False,
            "error": "audio_file_not_found"
        }


    if not path.is_file():

        return {
            "ok": False,
            "error": "audio_path_is_not_file"
        }


    try:

        size = path.stat().st_size

    except OSError:

        return {
            "ok": False,
            "error": "audio_file_unreadable"
        }


    if size <= 0:

        return {
            "ok": False,
            "error": "audio_file_empty"
        }


    return {
        "ok": True,
        "path": str(path),
        "size": size
    }


# ==========================================
# BEZPIECZNE ODCZYTANIE LICZBY
# ==========================================

def safe_float(
    value
):

    try:

        if value is None:
            return None

        return float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return None


# ==========================================
# JEDEN SEGMENT WHISPER
# ==========================================

def create_segment_result(
    segment
):

    text = str(
        getattr(
            segment,
            "text",
            ""
        )
        or
        ""
    ).strip()


    return {
        "start":
            safe_float(
                getattr(
                    segment,
                    "start",
                    None
                )
            ),

        "end":
            safe_float(
                getattr(
                    segment,
                    "end",
                    None
                )
            ),

        "text":
            text,

        "avg_logprob":
            safe_float(
                getattr(
                    segment,
                    "avg_logprob",
                    None
                )
            ),

        "no_speech_prob":
            safe_float(
                getattr(
                    segment,
                    "no_speech_prob",
                    None
                )
            )
    }


# ==========================================
# TRANSKRYPCJA AUDIO
# ==========================================
#
# Wynik przykładowy:
#
# {
#   "ok": True,
#   "text": "Ich heiße Moni.",
#   "language": "de",
#   "duration": 2.4,
#   "segments": [...]
# }
#
# ==========================================

def transcribe_audio(
    audio_path,
    language=WHISPER_LANGUAGE
):

    validation = validate_audio_file(
        audio_path
    )


    if not validation.get(
        "ok"
    ):

        return validation


    if not is_whisper_available():

        return {
            "ok": False,
            "error":
                "whisper_not_installed",

            "message":
                (
                    "faster-whisper is "
                    "not installed."
                )
        }


    try:

        model = get_whisper_model()


        print(
            "Nele Whisper: transcription started."
        )


        segments_generator, info = (
            model.transcribe(
                validation[
                    "path"
                ],

                language=language,

                beam_size=(
                    get_whisper_beam_size()
                ),

                vad_filter=(
                    get_whisper_vad_filter()
                ),

                condition_on_previous_text=False
            )
        )


        segments = []

        text_parts = []


        for segment in segments_generator:

            segment_result = (
                create_segment_result(
                    segment
                )
            )


            segment_text = (
                segment_result.get(
                    "text",
                    ""
                )
            )


            if segment_text:

                text_parts.append(
                    segment_text
                )


            segments.append(
                segment_result
            )


        text = " ".join(
            text_parts
        ).strip()


        detected_language = str(
            getattr(
                info,
                "language",
                language
            )
            or
            language
        )


        duration = safe_float(
            getattr(
                info,
                "duration",
                None
            )
        )


        language_probability = (
            safe_float(
                getattr(
                    info,
                    "language_probability",
                    None
                )
            )
        )


        print(
            "Nele Whisper: transcription:",
            text
        )


        return {
            "ok": True,

            "text":
                text,

            "language":
                detected_language,

            "language_probability":
                language_probability,

            "duration":
                duration,

            "audio_size":
                validation.get(
                    "size"
                ),

            "segments":
                segments
        }


    except Exception as error:

        print(
            "Nele Whisper error:",
            error
        )


        return {
            "ok": False,

            "error":
                "whisper_transcription_failed",

            "message":
                str(
                    error
                )
        }


# ==========================================
# PROSTA ODPOWIEDŹ:
# CO UŻYTKOWNIK POWIEDZIAŁ?
# ==========================================

def get_transcribed_text(
    audio_path,
    language=WHISPER_LANGUAGE
):

    result = transcribe_audio(
        audio_path,
        language
    )


    if not result.get(
        "ok"
    ):

        return ""


    return str(
        result.get(
            "text",
            ""
        )
    ).strip()
