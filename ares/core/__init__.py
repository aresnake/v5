# ares/core/__init__.py

try:
    from .logger import get_logger
    from .run_pipeline import main as run_pipeline
except ImportError as e:
    print(f"[Core Init] Erreur d'import : {e}")
