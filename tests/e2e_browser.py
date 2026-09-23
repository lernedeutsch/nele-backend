"""Browser -> frontend -> Flask -> PostgreSQL end-to-end test for Nele."""

import os
import time

import psycopg2
import requests
from playwright.sync_api import sync_playwright


FRONTEND_URL = os.environ.get(
    "NELE_E2E_FRONTEND_URL",
    "http://127.0.0.1:5500/nele.html",
)
BACKEND_URL = os.environ.get(
    "NELE_E2E_BACKEND_URL",
    "http://127.0.0.1:5000",
)
DATABASE_URL = os.environ["DATABASE_URL"]


def load_memory(session_id):
    connection = psycopg2.connect(DATABASE_URL)
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT memory
            FROM student_memory
            WHERE session_id = %s
            """,
            (session_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None
    finally:
        connection.close()


def wait_for_memory(session_id, expected_name, timeout=10):
    deadline = time.time() + timeout

    while time.time() < deadline:
        memory = load_memory(session_id)

        if isinstance(memory, dict):
            user_facts = memory.get("user_facts") or {}

            if (
                memory.get("name") == expected_name
                or user_facts.get("name") == expected_name
            ):
                return memory

        time.sleep(0.25)

    raise AssertionError(
        "Learner memory was not persisted to PostgreSQL."
    )


def cleanup(session_id):
    connection = psycopg2.connect(DATABASE_URL)
    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT to_regclass('public.student_memory')"
        )
        table_name = cursor.fetchone()[0]

        if table_name:
            cursor.execute(
                """
                DELETE FROM student_memory
                WHERE session_id = %s
                """,
                (session_id,),
            )
            connection.commit()

        cursor.close()
    finally:
        connection.close()


def wait_for_last_nele(page, expected, timeout=15000):
    page.wait_for_function(
        """expected => {
            const items = [
                ...document.querySelectorAll('.message-nele')
            ];
            if (!items.length) {
                return false;
            }
            return items[items.length - 1]
                .innerText
                .includes(expected);
        }""",
        arg=expected,
        timeout=timeout,
    )

    return page.locator(
        ".message-nele"
    ).last.inner_text()


def send_and_wait(page, message, expected, timeout=15000):
    before = page.locator(
        ".message-nele"
    ).count()

    page.fill(
        "#message-input",
        message,
    )
    page.click(
        "#send-btn"
    )

    page.wait_for_function(
        """data => {
            const items = [
                ...document.querySelectorAll('.message-nele')
            ];
            if (items.length <= data.before) {
                return false;
            }
            return items[items.length - 1]
                .innerText
                .includes(data.expected);
        }""",
        arg={
            "before": before,
            "expected": expected,
        },
        timeout=timeout,
    )

    return page.locator(
        ".message-nele"
    ).last.inner_text()


def verify_backend_http():
    session_id = "e2e-http-backend-check"

    cleanup(session_id)

    response = requests.post(
        f"{BACKEND_URL}/welcome",
        json={"session_id": session_id},
        timeout=10,
    )

    assert response.status_code == 200, (
        response.status_code,
        response.text,
    )

    memory = load_memory(session_id)
    assert isinstance(memory, dict)

    cleanup(session_id)


def main():
    test_name = "Monika"
    session_id = None

    verify_backend_http()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            page.on(
                "console",
                lambda msg: print(
                    "BROWSER CONSOLE:",
                    msg.type,
                    msg.text,
                ),
            )
            page.on(
                "requestfailed",
                lambda req: print(
                    "BROWSER REQUEST FAILED:",
                    req.url,
                    req.failure,
                ),
            )

            page.add_init_script(
                f"window.NELE_BACKEND_URL = {BACKEND_URL!r};"
            )

            page.goto(
                FRONTEND_URL,
                wait_until="domcontentloaded",
            )

            browser_health = page.evaluate(
                """async backendUrl => {
                    try {
                        const response = await fetch(
                            backendUrl + '/health'
                        );
                        return {
                            status: response.status,
                            text: await response.text()
                        };
                    } catch (error) {
                        return {
                            status: 0,
                            text: String(error)
                        };
                    }
                }""",
                BACKEND_URL,
            )

            print(
                "BROWSER HEALTH:",
                browser_health,
            )

            assert browser_health["status"] == 200

            wait_for_last_nele(
                page,
                "Wie heißt du?",
                timeout=10000,
            )

            session_id = page.evaluate(
                "() => localStorage.getItem('nele_session_id')"
            )

            assert session_id
            assert session_id != "default"

            # ----------------------------------
            # ERSTER KONTAKT / ONBOARDING
            # ----------------------------------
            send_and_wait(
                page,
                "Ich heißen Monika",
                "Ich heiße Monika",
            )
            send_and_wait(
                page,
                "Ich bin Monika",
                "Woher kommst du?",
            )

            memory = wait_for_memory(
                session_id,
                test_name,
            )
            assert memory.get("onboarding_step") == 2

            # Unterbrochenes Onboarding muss nach Reload
            # mit demselben Benutzer weitergehen.
            page.reload(
                wait_until="domcontentloaded"
            )
            wait_for_last_nele(
                page,
                "Woher kommst du?",
            )

            same_session_id = page.evaluate(
                "() => localStorage.getItem('nele_session_id')"
            )
            assert same_session_id == session_id

            send_and_wait(
                page,
                "Ich komme Polen",
                "Ich komme aus Polen",
            )
            send_and_wait(
                page,
                "Ich komme aus Polen",
                "Wo wohnst du?",
            )
            send_and_wait(
                page,
                "Ich wohnen in Heidelberg",
                "Ich wohne in Heidelberg",
            )
            send_and_wait(
                page,
                "Ich wohne in Heidelberg",
                "Bist du bereit?",
            )

            # Nach abgeschlossenem Onboarding beginnt
            # ein neues Treffen mit dem bekannten Benutzer.
            page.reload(
                wait_until="domcontentloaded"
            )
            wait_for_last_nele(
                page,
                "Wie geht es dir?",
            )

            send_and_wait(
                page,
                "gut",
                "Es ist Morgen",
            )

            # ----------------------------------
            # LEKTION 1 / BEGRÜSSUNGEN + FEHLER
            # ----------------------------------
            send_and_wait(page, "Gute Morgen", "Guten Morgen")
            send_and_wait(page, "Guten Nacht", "Guten Morgen")
            send_and_wait(page, "h", "Guten Morgen")
            send_and_wait(page, "k", "Guten Morgen")
            send_and_wait(page, "g", "Guten Morgen")
            send_and_wait(
                page,
                "Guten Morgen",
                "Es ist Tag",
            )

            send_and_wait(page, "p", "Guten Tag")
            send_and_wait(page, "o", "Guten Tag")
            send_and_wait(
                page,
                "Guten Tag",
                "Abend",
            )

            # Reload mitten in der Lektion:
            # zuerst Fehlertraining, danach genau an
            # der unterbrochenen Stelle weiter.
            page.reload(
                wait_until="domcontentloaded"
            )
            wait_for_last_nele(
                page,
                "Wie geht es dir?",
            )

            first_review = send_and_wait(
                page,
                "gut",
                "Welche Antwort passt hier?",
            )
            assert "Guten Morgen" in first_review

            send_and_wait(
                page,
                "2",
                "Sag die richtige Antwort",
            )
            second_review = send_and_wait(
                page,
                "Guten Morgen",
                "Welche Antwort passt hier?",
            )
            assert "Guten Tag" in second_review

            send_and_wait(
                page,
                "2",
                "Sag die richtige Antwort",
            )
            resumed = send_and_wait(
                page,
                "Guten Tag",
                "Abend",
            )
            assert "Was sagst du?" in resumed

            # Restliche Begrüßungen mit neuen Fehlern.
            send_and_wait(page, "h", "Guten Abend")
            send_and_wait(page, "j", "Guten Abend")
            send_and_wait(
                page,
                "Guten Abend",
                "zu einem Freund",
            )

            send_and_wait(page, "j", "Hallo")
            send_and_wait(page, "k", "Hallo")
            send_and_wait(
                page,
                "Hallo",
                "Du gehst",
            )

            send_and_wait(page, "x", "Tschüss")
            send_and_wait(
                page,
                "Tschüss",
                "Ich sage: „Guten Morgen!“",
            )
            send_and_wait(
                page,
                "Hallo",
                "Guten Morgen",
            )
            send_and_wait(
                page,
                "Guten Morgen",
                "Ich stelle mich vor",
            )

            # ----------------------------------
            # ICH STELLE MICH VOR
            # ----------------------------------
            send_and_wait(
                page,
                "ja",
                "Guten Morgen!",
            )
            send_and_wait(
                page,
                "Guten Morgen",
                "Wie heißt du?",
            )
            send_and_wait(
                page,
                "testimony",
                "Ich heiße Monika",
            )
            send_and_wait(
                page,
                "Ich heiße Monika",
                "Frag mich",
            )
            send_and_wait(
                page,
                "wer bist du",
                "Wie heißt du?",
            )
            send_and_wait(
                page,
                "Wie heißt du",
                "Buchstabiere bitte deinen Namen",
            )
            send_and_wait(
                page,
                "Monika",
                "Buchstabe für Buchstabe",
            )
            send_and_wait(
                page,
                "m o n i k a",
                "Jetzt höflich",
            )
            send_and_wait(
                page,
                "Wie heißt du",
                "Wie heißen Sie?",
            )
            send_and_wait(
                page,
                "Wie heißen Sie",
                "Das deutsche Alphabet",
            )

            # ----------------------------------
            # DAS DEUTSCHE ALPHABET
            # ----------------------------------
            send_and_wait(
                page,
                "ja",
                "Hör zu: A",
            )
            send_and_wait(page, "g", "Sag bitte: „A“")
            send_and_wait(
                page,
                "A",
                "Jetzt B",
            )
            send_and_wait(page, "j", "Sag bitte: „B“")
            send_and_wait(
                page,
                "B",
                "Buchstabe: M",
            )
            send_and_wait(page, "u", "Das ist M")
            send_and_wait(
                page,
                "M",
                "Umlaute",
            )
            send_and_wait(
                page,
                "a o u",
                "Ä, Ö und Ü",
            )
            send_and_wait(
                page,
                "ä ö ü",
                "auch ß",
            )
            send_and_wait(
                page,
                "ss",
                "Eszett",
            )
            send_and_wait(
                page,
                "ß",
                "Buchstabiere bitte deinen Namen",
            )
            send_and_wait(
                page,
                "Monika",
                "Buchstaben einzeln",
            )
            final_reply = send_and_wait(
                page,
                "m o n i k a",
                "Lektion 1 ist fertig",
            )

            assert "Hörübung" not in final_reply
            assert "Schreibübung" not in final_reply

            memory = load_memory(
                session_id
            )
            assert isinstance(memory, dict)

            lesson_progress = (
                memory.get("lesson_progress")
                or {}
            )
            lessons = (
                lesson_progress.get("lessons")
                or {}
            )
            lesson_one = (
                lessons.get("A1:1")
                or {}
            )

            assert lesson_one.get("completed") is True
            assert set(
                lesson_one.get(
                    "completed_sections",
                    [],
                )
            ) == {
                "Wir begrüßen uns",
                "Ich stelle mich vor",
                "Das deutsche Alphabet",
            }

            error_memory = (
                memory.get("error_memory")
                or {}
            )
            assert error_memory

            browser.close()

        print(
            "E2E OK: first open -> onboarding -> "
            "Lektion 1 -> Fehlertraining -> PostgreSQL"
        )

    finally:
        if session_id:
            cleanup(session_id)


if __name__ == "__main__":
    main()
