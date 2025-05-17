from logging import getLogger, DEBUG, basicConfig
from pathlib import Path

PROJECT_NAME = "Davit-Capstone"

basicConfig()

logger = getLogger()

logger.setLevel(DEBUG)
PACKAGE_ROOT = Path(__file__).resolve().parent
