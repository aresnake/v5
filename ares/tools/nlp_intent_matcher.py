# ares/tools/nlp_intent_matcher.py
"""
nlp_intent_matcher.py – Correspondance floue/NLP pour les intents Blade.
Utilise spaCy si dispo (fr_core_news_sm), sinon fallback difflib.
- Prend en compte: 'phrase' (str), 'phrases' (List[str]), 'aliases' (List[str])
- Normalise: minuscules + suppression des accents
- Seuil par défaut abaissé à 0.50 pour mieux capter les tournures FR
- Petit lexique de couleurs pour booster les correspondances
"""

import difflib
import re
import unicodedata

# Chargement spaCy si dispo
try:
    import spacy

    try:
        nlp_fr = spacy.load("fr_core_news_sm")
    except OSError:
        nlp_fr = None
except Exception:
    nlp_fr = None

STOPWORDS = {
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "de",
    "du",
    "en",
    "au",
    "aux",
    "à",
    "a",
    "et",
    "met",
    "mets",
    "mettre",
    "changer",
    "change",
    "passe",
    "l",
    "'",  # tolérance basique
}

COLOR_SYNONYMS = {
    "rouge": {"rouge", "red"},
    "vert": {"vert", "verte", "green"},
    "bleu": {"bleu", "bleue", "blue"},
    "jaune": {"jaune", "yellow"},
    "blanc": {"blanc", "blanche", "white"},
    "noir": {"noir", "noire", "black"},
    "orange": {"orange"},
    "violet": {"violet", "violette", "purple"},
}


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _norm(s: str) -> str:
    s = _strip_accents(s or "").lower().strip()
    # retire stopwords basiques
    toks = [t for t in re.split(r"\W+", s) if t and t not in STOPWORDS]
    return " ".join(toks)


def _iter_variants(intent: dict) -> list[str]:
    out = []
    p = intent.get("phrase")
    if isinstance(p, str) and p.strip():
        out.append(p)
    for key in ("phrases", "aliases"):
        lst = intent.get(key)
        if isinstance(lst, list):
            out.extend([x for x in lst if isinstance(x, str) and x.strip()])
    # fallback sur le name si pas de phrase du tout
    if not out and isinstance(intent.get("name"), str):
        out.append(intent["name"])
    # normalisation
    uniq = []
    seen = set()
    for v in out:
        nv = _norm(v)
        if nv and nv not in seen:
            uniq.append(nv)
            seen.add(nv)
    return uniq


def _boost_color(phrase_n: str, intent: dict, base_score: float) -> float:
    # Si la phrase mentionne une couleur, on booste les intents contenant cette couleur.
    for cname, syns in COLOR_SYNONYMS.items():
        if any(s in phrase_n.split() for s in syns):
            # présence du mot-couleur dans intent (name/phrases)
            blob = " ".join(_iter_variants(intent) + [_norm(intent.get("name", ""))])
            if cname in blob.split():
                return min(1.0, base_score + 0.15)
    return base_score


def similarity(phrase: str, candidate: str) -> float:
    if nlp_fr:
        # spaCy: similarité basique
        d1 = nlp_fr(phrase)
        d2 = nlp_fr(candidate)
        return float(d1.similarity(d2))
    # Fallback difflib
    return float(difflib.SequenceMatcher(None, phrase, candidate).ratio())


def match_intent(
    phrase: str, intents: list[dict], threshold: float = 0.50
) -> tuple[dict | None, float]:
    phrase_n = _norm(phrase)
    best_score = 0.0
    best_intent = None

    # Construire la liste des variantes normalisées par intent
    variants = [(intent, _iter_variants(intent)) for intent in intents]

    for intent, vs in variants:
        # score max sur toutes les variantes de cet intent
        local_best = 0.0
        for v in vs:
            local_best = max(local_best, similarity(phrase_n, v))
        # Boost couleur si nécessaire
        local_best = _boost_color(phrase_n, intent, local_best)

        if local_best > best_score:
            best_score = local_best
            best_intent = intent

    if best_score >= threshold:
        return best_intent, best_score
    return None, best_score


if __name__ == "__main__":
    # test rapide
    sample = [
        {"name": "changer_couleur_rouge", "phrases": ["change en rouge"]},
        {"name": "ajouter_cube", "phrases": ["ajoute un cube"]},
    ]
    intent, score = match_intent("mets en rouge", sample)
    print("→", intent, score)
