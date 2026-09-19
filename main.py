"""LEGACY CLI entrypoint.

Production Nele runs from server/app.py via gunicorn server.app:app.
This file is intentionally kept for historical/local experiments only.
"""

import os


if __name__ == "__main__":
    if str(
        os.environ.get(
            "NELE_ENABLE_LEGACY_CLI",
            "",
        )
    ).strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        raise SystemExit(
            "Legacy Nele CLI is disabled. "
            "Production entrypoint: gunicorn server.app:app. "
            "Set NELE_ENABLE_LEGACY_CLI=1 only for an intentional local legacy run."
        )

    from brain.core import start

    start()
