# ares/core/intent_parser.py
"""
intent_parser.py – Analyse une phrase et extrait un intent
Basé sur le fichier config/voice_config.yaml
Avec fallback NLP si aucun match exact trouvé.
"""

from __future__ import annotations

import os
import io
import time
import yaml
import difflib
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from ares.core.logger import get_logger

# ⚙️ Respect de la structure validée: ares/config/voice_config.yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "voice_config.yaml")
CONFIG_PATH = os.path.normpath(CONFIG_PATH)

log = get_logger("IntentParser")

# Cache en mémoire + mtime pour reload auto
_intent_cache: Optional[List[Dict[str, Any]]] = None
_intent_cache_mtime: Optional[float] = None


# ---------------------------
# Utils de normalisation texte
# ---------------------------

def _strip_accents(s: str) -> str:
    # Sans dépendance externe: unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _norm_txt(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().lower()
    s = _strip_accents(s)
    # Optionnel: réduire espaces multiples
    while "  " in s:
        s = s.replace("  ", " ")
    return s


# ---------------------------
# Lecture YAML + cache
# ---------------------------

def _read_yaml(path: str) -> List[Dict[str, Any]]:
    with io.open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        log.warning("⚠️ Le fichier voice_config.yaml ne contient pas une liste d'intents.")
        return []
    return [d for d in data if isinstance(d, dict)]


def load_intents(force_reload: bool = False) -> List[Dict[str, Any]]:
    """
    Charge ou retourne en cache les intents YAML.
    Reload automatique si le fichier a changé sur disque.
    """
    global _intent_cache, _intent_cache_mtime

    try:
        mtime = os.path.getmtime(CONFIG_PATH)
    except Exception as e:
        log.error(f"❌ Impossible d'accéder à '{CONFIG_PATH}': {e}")
        return []

    if (
        force_reload
        or _intent_cache is None
        or _intent_cache_mtime is None
        or mtime > _intent_cache_mtime
    ):
        try:
            intents = _read_yaml(CONFIG_PATH)
            _intent_cache = intents
            _intent_cache_mtime = mtime
            log.info(f"🔄 Intents rechargés ({len(intents)}) depuis {CONFIG_PATH}")
        except Exception as e:
            log.error(f"❌ Erreur de lecture YAML: {e}")
            return []

    return _intent_cache or []


def invalidate_cache() -> None:
    """Force un rechargement au prochain appel de load_intents()."""
    global _intent_cache, _intent_cache_mtime
    _intent_cache = None
    _intent_cache_mtime = None


# ---------------------------
# Matching helpers
# ---------------------------

def _iter_all_phrases(intent: Dict[str, Any]) -> List[str]:
    """
    Retourne toutes les variantes textuelles d'un intent:
    - 'phrase' (str) – rétro-compat
    - 'phrases' (List[str])
    - 'aliases' (List[str]) – champ optionnel
    """
    out: List[str] = []
    p = intent.get("phrase")
    if isinstance(p, str) and p.strip():
        out.append(p)

    pl = intent.get("phrases")
    if isinstance(pl, list):
        out.extend([x for x in pl if isinstance(x, str) and x.strip()])

    al = intent.get("aliases")
    if isinstance(al, list):
        out.extend([x for x in al if isinstance(x, str) and x.strip()])

    # Dédup + ordre stable
    seen = set()
    uniq = []
    for s in out:
        if s not in seen:
            uniq.append(s)
            seen.add(s)
    return uniq


def _standardize_intent(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renvoie un dict prêt pour l'exécution par intent_executor:
    { 'name', 'operator', 'params', ...meta }
    """
    result = dict(raw)  # shallow copy
    result.setdefault("name", raw.get("id") or "intent_sans_nom")
    result.setdefault("operator", None)
    result["params"] = result.get("params", {}) or {}
    return result


def _exact_match(phrase_norm: str, intents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for it in intents:
        for variant in _iter_all_phrases(it):
            if _norm_txt(variant) == phrase_norm:
                return _standardize_intent(it)
    return None


def _fuzzy_match_fallback(phrase: str, intents: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    """
    Fallback fuzzy local (difflib) si module NLP indisponible.
    Retourne (intent, score[0..1])
    """
    candidates: List[Tuple[str, Dict[str, Any]]] = []
    for it in intents:
        for variant in _iter_all_phrases(it):
            candidates.append((_norm_txt(variant), it))

    if not candidates:
        return None, 0.0

    phrase_n = _norm_txt(phrase)
    keys = [k for (k, _) in candidates]
    best = difflib.get_close_matches(phrase_n, keys, n=1, cutoff=0.6)
    if not best:
        return None, 0.0

    best_key = best[0]
    for k, it in candidates:
        if k == best_key:
            return _standardize_intent(it), difflib.SequenceMatcher(None, phrase_n, k).ratio()

    return None, 0.0


def _nlp_match(phrase: str, intents: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    """
    Utilise ares.tools.nlp_intent_matcher si disponible.
    Doit exposer: match_intent(phrase: str, intents: List[dict]) -> Tuple[dict|None, float]
    """
    try:
        from ares.tools import nlp_intent_matcher as nlp
    except Exception:
        return _fuzzy_match_fallback(phrase, intents)

    try:
        best, score = nlp.match_intent(phrase, intents)
        if best:
            return _standardize_intent(best), float(score or 0.0)
        return None, float(score or 0.0)
    except Exception as e:
        log.warning(f"⚠️ NLP matcher indisponible/erreur → fallback difflib: {e}")
        return _fuzzy_match_fallback(phrase, intents)


# ---------------------------
# Public API
# ---------------------------

def parse_intent(phrase: str) -> Optional[Dict[str, Any]]:
    """
    Reçoit une phrase, retourne l'intent correspondant si trouvé.
    Priorités:
      1) Matching exact (phrases/aliases normalisés, sans accents)
      2) Matching NLP (ou fuzzy fallback)
    """
    if not phrase or not str(phrase).strip():
        log.warning("🛑 Phrase vide reçue.")
        return None

    phrase_clean = _norm_txt(phrase)
    intents = load_intents()

    # 1️⃣ Matching exact
    exact = _exact_match(phrase_clean, intents)
    if exact:
        log.info(f"✅ Intent trouvé (exact): {exact.get('name')} pour phrase '{phrase}'")
        return exact

    # 2️⃣ Matching NLP / fuzzy
    best_intent, score = _nlp_match(phrase, intents)
    if best_intent:
        log.info(f"🤖 Intent trouvé (NLP/Fuzzy {score:.2f}): {best_intent.get('name')} pour phrase '{phrase}'")
        return best_intent

    log.warning(f"❓ Aucun intent trouvé pour la phrase: '{phrase}' (score max {score:.2f})")
    return None


# ---------------------------
# Dev helpers
# ---------------------------

def debug_preview(limit: int = 10) -> None:
    """Affiche un aperçu des intents chargés (pour debug)."""
    intents = load_intents()
    log.info(f"🧭 {len(intents)} intents chargés depuis {CONFIG_PATH}")
    for i, it in enumerate(intents[:limit]):
        log.info(f"  - {i+1}. {it.get('name')} | operator={it.get('operator')}")
