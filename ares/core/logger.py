# ✅ Fichier : ares/core/logger.py (UTF-8 safe logger)

import io
import logging
import os
import sys

# 🔹 Forcer stdout/stderr en UTF-8 pour éviter les caractères cassés (Windows CP1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

LOG_FORMAT = "[%(asctime)s][%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_logger_cache = {}


def get_logger(name="Blade"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    fh = logging.FileHandler(os.path.join(logs_dir, "blade.log"), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()  # console
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


def clear_logs():
    """Clear all log files."""
    logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    if os.path.exists(logs_dir):
        for f in os.listdir(logs_dir):
            try:
                os.remove(os.path.join(logs_dir, f))
            except OSError:
                pass
