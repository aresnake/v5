# tests/test_run_pipeline.py

"""
Test de la pipeline principale de Blade
Vérifie que l'enchaînement phrase → intent → exécution fonctionne
"""

import unittest

from ares.core.run_pipeline import main as run_pipeline


class TestRunPipeline(unittest.TestCase):
    def test_basic_intent(self):
        phrase = "ajoute un cube"
        try:
            run_pipeline(phrase, mode="text")
            success = True
        except Exception as e:
            print(f"Erreur rencontrée : {e}")
            success = False

        self.assertTrue(success, "L'exécution de la pipeline a échoué.")


if __name__ == '__main__':
    unittest.main()
