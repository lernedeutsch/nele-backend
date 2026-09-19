"""Browser -> frontend -> Flask -> PostgreSQL end-to-end test for Nele."""

import os
import time

import psycopg2
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


def main():
    test_name = "E2E-Moni-Test"
    session_id = None

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            page.add_init_script(
                f"window.NELE_BACKEND_URL = {BACKEND_URL!r};"
            )

            page.goto(
                FRONTEND_URL,
                wait_until="domcontentloaded",
            )

            page.wait_for_function(
                """() => {
                    const text =
                        document.querySelector('#messages')?.innerText || '';
                    return text.includes('Wie heißt du?');
                }""",
                timeout=15000,
            )

            session_id = page.evaluate(
                "() => localStorage.getItem('nele_session_id')"
            )

            assert session_id
            assert session_id != "default"

            page.fill(
                "#message-input",
                test_name,
            )
            page.click(
                "#send-btn"
            )

            page.wait_for_function(
                """() => {
                    const text =
                        document.querySelector('#messages')?.innerText || '';
                    return text.includes('Woher kommst du?');
                }""",
                timeout=15000,
            )

            memory = wait_for_memory(
                session_id,
                test_name,
            )

            assert memory.get("onboarding_step") == 2

            page.reload(
                wait_until="domcontentloaded"
            )

            page.wait_for_function(
                """name => {
                    const text =
                        document.querySelector('#messages')?.innerText || '';
                    return text.includes(name)
                        && text.includes('Woher kommst du?');
                }""",
                arg=test_name,
                timeout=15000,
            )

            same_session_id = page.evaluate(
                "() => localStorage.getItem('nele_session_id')"
            )

            assert same_session_id == session_id

            browser.close()

        print(
            "E2E OK: browser -> frontend -> backend -> PostgreSQL -> reload"
        )

    finally:
        if session_id:
            cleanup(session_id)


if __name__ == "__main__":
    main()
