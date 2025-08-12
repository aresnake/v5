# ares/codex/run_codex_pipeline.py

"""
run_codex_pipeline.py
Enchaîne toute la pipeline d'apprentissage et de suggestions IA Codex :
- generate_learning_prompts
- codex_suggester
- suggestions_pending_generator
"""

import subprocess
import os
from ares.logger import get_logger

log = get_logger("CodexPipeline")
BASE = os.path.dirname(__file__)

def run_script(path):
    full_path = os.path.join(BASE, path)
    log.info(f"▶️ Exécution de {path} ...")
    subprocess.run(["python", full_path], check=True)

def main():
    try:
        run_script("generate_learning_prompts.py")
        run_script("codex_suggester.py")
        run_script("../tools/suggestions_pending_generator.py")
        log.info("✅ Pipeline Codex terminée avec succès.")
    except Exception as e:
        log.error(f"❌ Erreur dans le pipeline Codex : {e}")

if __name__ == "__main__":
    main()
