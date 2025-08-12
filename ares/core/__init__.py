
# ares/core/__init__.py

try:
    from .run_pipeline import main as run_pipeline
    from .logger import get_logger
except ImportError as e:
    print(f"[Core Init] Erreur d'import : {e}")
