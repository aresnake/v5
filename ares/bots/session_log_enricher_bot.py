from ares.tools.operator_classifier import classify_operator

def enrich_log(intent: dict, mode="voice"):
    if not intent:
        return
    enriched = {
        "name": intent.get("name"),
        "phrase": intent.get("phrase"),
        "operator": intent.get("operator"),
        "params": intent.get("params", {}),
        "type": classify_operator(intent.get("operator", "")),
        "mode": mode,
    }
    return enriched
