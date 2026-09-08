# ==========================================
# NELE – TRWAŁA PAMIĘĆ UCZNIA
# POSTGRESQL
# ==========================================

import os
import json

import psycopg2


# ==========================================
# POŁĄCZENIE Z BAZĄ
# ==========================================

def get_database_connection():

    database_url = os.environ.get(
        "DATABASE_URL"
    )

    if not database_url:
        return None

    return psycopg2.connect(
        database_url
    )


# ==========================================
# UTWORZENIE TABELI
# ==========================================

def initialize_persistent_memory():

    connection = get_database_connection()

    if connection is None:
        print(
            "DATABASE_URL not found."
        )
        return False

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS student_memory (
                session_id TEXT PRIMARY KEY,
                memory JSONB NOT NULL DEFAULT '{}'::jsonb,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

        cursor.close()

        return True

    except Exception as error:

        print(
            f"Persistent memory initialization error: {error}"
        )

        connection.rollback()

        return False

    finally:

        connection.close()


# ==========================================
# POBRANIE PAMIĘCI UCZNIA
# ==========================================

def load_persistent_memory(
    session_id
):

    if not session_id:
        session_id = "default"

    connection = get_database_connection()

    if connection is None:
        return {}

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT memory
            FROM student_memory
            WHERE session_id = %s
            """,
            (
                session_id,
            )
        )

        row = cursor.fetchone()

        cursor.close()

        if not row:
            return {}

        memory = row[0]

        if isinstance(
            memory,
            dict
        ):
            return memory

        if isinstance(
            memory,
            str
        ):

            return json.loads(
                memory
            )

        return {}

    except Exception as error:

        print(
            f"Persistent memory load error: {error}"
        )

        return {}

    finally:

        connection.close()


# ==========================================
# ZAPIS PAMIĘCI UCZNIA
# ==========================================

def save_persistent_memory(
    session_id,
    memory
):

    if not session_id:
        session_id = "default"

    if memory is None:
        memory = {}

    connection = get_database_connection()

    if connection is None:
        return False

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO student_memory (
                session_id,
                memory,
                updated_at
            )
            VALUES (
                %s,
                %s::jsonb,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (session_id)
            DO UPDATE SET
                memory = EXCLUDED.memory,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                session_id,
                json.dumps(
                    memory,
                    ensure_ascii=False
                )
            )
        )

        connection.commit()

        cursor.close()

        return True

    except Exception as error:

        print(
            f"Persistent memory save error: {error}"
        )

        connection.rollback()

        return False

    finally:

        connection.close()


# ==========================================
# USUNIĘCIE PAMIĘCI UCZNIA
# ==========================================

def delete_persistent_memory(
    session_id
):

    if not session_id:
        return False

    connection = get_database_connection()

    if connection is None:
        return False

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM student_memory
            WHERE session_id = %s
            """,
            (
                session_id,
            )
        )

        connection.commit()

        cursor.close()

        return True

    except Exception as error:

        print(
            f"Persistent memory delete error: {error}"
        )

        connection.rollback()

        return False

    finally:

        connection.close()
