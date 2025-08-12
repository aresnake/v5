"""
ContextBuilder – Extrait les blocs utiles pour gnrer ou corriger des intents automatiquement
"""
import os

def extract_context_snippets(base_path=".", max_files=10):
    snippets = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith(".py") and "__init__" not in f:
                full_path = os.path.join(root, f)
                with open(full_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    snippets.append(f"# Fichier: {f}\n" + content[:1000])
                if len(snippets) >= max_files:
                    break
    return "\n\n".join(snippets)
