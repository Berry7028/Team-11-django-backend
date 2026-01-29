#!/usr/bin/env python
"""Django's command-line utility for administrative tasks (new backend project)."""
import os
import sys
from pathlib import Path

# backendディレクトリをPythonパスに追加
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Some environments export DJANGO_SETTINGS_MODULE=backend.config.settings,
# which is not importable when running from the backend/ directory.
_settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
if _settings_module in {"backend", "backend.settings", "backend.config.settings"}:
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"


def main() -> None:
    """Run administrative tasks for the backend project."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
