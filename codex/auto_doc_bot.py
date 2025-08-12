"""
AutoDocBot – Gnre de la documentation depuis le code source
"""

from codex.agent_codex import call_codex


def generate_doc_from_code(code: str, filename: str) -> str:
    prompt = f"""Voici le contenu du fichier {filename} :

{code}

Gnre une documentation claire, en Markdown, expliquant les fonctions principales du fichier.
"""
    return call_codex(prompt)
