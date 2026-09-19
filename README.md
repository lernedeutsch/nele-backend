# Nele Backend — produkcja

To repozytorium jest **jedynym produkcyjnym backendem Nele**.

## Produkcyjna architektura

`lernedeutsch/deutschsprechen`
→ `https://nele-backend.onrender.com`
→ PostgreSQL

Produkcyjny frontend:
`https://lernedeutsch.github.io/deutschsprechen/nele.html`

Jedynym identyfikatorem ucznia używanym przez aktywny frontend jest:
`nele_session_id`

## Produkcyjny entrypoint

Aplikacja WWW to:

`server/app.py`

Uruchomienie produkcyjne:

`gunicorn server.app:app`

Plik `main.py` nie jest produkcyjnym entrypointem.

## Stan sesji

Tymczasowy stan rozmowy jest centralizowany w:

`brain/logic/session_state.py`

`Neu anfangen` rozpoczyna nową rozmowę tego samego ucznia:
- zachowuje PostgreSQL i trwałą pamięć nauki,
- zachowuje postęp lekcji, słownictwo, błędy i wymowę,
- czyści aktywne zadanie Nele 3,
- czyści stary aktywny krok lesson engine,
- czyści stare tryby vocabulary/error/review,
- nie wywołuje pełnego resetu użytkownika.

## Bezpieczeństwo

CORS domyślnie zezwala na:
- `https://lernedeutsch.github.io`
- lokalne `127.0.0.1:5500` i `localhost:5500`

Można nadpisać listę przez:
`CORS_ORIGINS`

Pełne kasowanie pamięci przez `/reset` i `/api/reset/<student_id>`
jest domyślnie zablokowane. Do ręcznego, administracyjnego użycia wymagane są równocześnie:
- `NELE_ENABLE_DESTRUCTIVE_RESET=true`
- `NELE_RESET_SECRET=<sekret>`
- nagłówek `X-Nele-Reset-Token` z tym samym sekretem.

Aktywny frontend nie korzysta z pełnego resetu.

## Pamięć

Trwała pamięć ucznia korzysta z `DATABASE_URL` i PostgreSQL.
Brak udanej inicjalizacji bazy nie jest już zapisywany jako udana inicjalizacja.

## Głos

- zwykły mikrofon frontendu: Web Speech API,
- prawdziwe nagranie wymowy: MediaRecorder → `/chat` → faster-whisper,
- przeglądarkowa mowa Nele: SpeechSynthesis,
- Piper pozostaje opcjonalnym backendowym TTS i wymaga prawdziwych plików ustawionych przez `PIPER_PATH` i `PIPER_MODEL_PATH`.

## Legacy — nie jest produkcją

Poniższe moduły są zachowane wyłącznie historycznie/lokalnie i nie należą do produkcyjnego przepływu Flask:
- `main.py`
- `brain/core.py`
- `speech/listener.py`
- `brain/model_service.py`

Nie są usuwane, ale nie powinny być używane do uruchamiania produkcyjnej Nele.

Repo `nele-backend-3` pozostaje eksperymentalne i nie jest backendem aktywnego frontendu.
