"""
IntentsGenerator – Propose des intents vocaux  partir de logs ou prompts
"""
from codex.agent_codex import call_codex
from codex.context_builder import extract_context_snippets

def generate_intents_from_prompt(prompt: str):
    context = extract_context_snippets()
    full_prompt = f"""Tu es un expert Blender. Gnre un bloc YAML d’intents  partir du texte suivant :

Contexte :
{context}

Texte utilisateur :
{prompt}

Rponds uniquement par un bloc YAML.
"""
    return call_codex(full_prompt)
