from ares.tools.nlp_intent_matcher import match_intent

def test_match_red():
    intents = [
        {"name": "changer_couleur_rouge", "phrases": ["change en rouge"]},
        {"name": "ajouter_cube", "phrases": ["ajoute un cube"]},
    ]
    intent, score = match_intent("mets en rouge", intents)
    assert intent and intent["name"] == "changer_couleur_rouge"
    assert score >= 0.50
