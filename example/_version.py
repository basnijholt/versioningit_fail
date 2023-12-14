from pathlib import Path

import versioningit

PROJECT_DIR = Path(__file__).parent.parent


def _get_version() -> str:
    return versioningit.get_version(project_dir=PROJECT_DIR)

__version__ = _get_version()
