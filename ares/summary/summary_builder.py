# ares/summary/summary_builder.py

"""
SummaryBuilder â€“ GÃ©nÃ¨re un rÃ©sumÃ© structurÃ© des intents exÃ©cutÃ©s (succÃ¨s, Ã©checs, erreurs)
CrÃ©e un fichier .json ou .md dans le dossier summary/ pour chaque session
"""

import json
import os
from datetime import datetime

from ares.core.logger import get_logger

log = get_logger("SummaryBuilder")
SUMMARY_DIR = os.path.join(os.path.dirname(__file__), "..", "summary")

os.makedirs(SUMMARY_DIR, exist_ok=True)


def build_summary_dict(results: list[tuple[str, str]], session_id: str) -> dict:
    """Construit le dictionnaire rÃ©sumÃ© Ã  partir des rÃ©sultats."""
    summary = {
        "session": session_id,
        "results": results,
        "success_count": sum(1 for r in results if r[1] == "success"),
        "failed_count": sum(1 for r in results if r[1] == "failed"),
        "not_found_count": sum(1 for r in results if r[1] == "not_found"),
    }
    summary["total_count"] = len(results)
    return summary


def save_session_summary(results: list[tuple[str, str]], session_id: str = None):
    """
    Enregistre un rÃ©sumÃ© des intents :
    [ ("phrase", "success"|"failed"|"not_found") ]
    GÃ©nÃ¨re 2 fichiers : .json (machine) + .md (humain)
    """
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary = build_summary_dict(results, session_id)

    # ðŸ”¹ Sauvegarde JSON
    json_path = os.path.join(SUMMARY_DIR, f"session_{session_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # ðŸ”¸ Sauvegarde Markdown lisible
    md_path = os.path.join(SUMMARY_DIR, f"session_{session_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# RÃ©sumÃ© de session â€“ {session_id}\n\n")
        f.write(f"- âœ… SuccÃ¨s : {summary['success_count']}\n")
        f.write(f"- âŒ Ã‰checs : {summary['failed_count']}\n")
        f.write(f"- ðŸ¤· Non trouvÃ©s : {summary['not_found_count']}\n")
        f.write(f"- ðŸ”¢ Total : {summary['total_count']}\n\n")
        f.write("## DÃ©tails\n")
        for phrase, status in summary["results"]:
            emoji = {"success": "âœ…", "failed": "âŒ", "not_found": "ðŸ¤·"}.get(status, "â€¢")
            f.write(f"- {emoji} `{phrase}` â†’ `{status}`\n")

    log.info(f"ðŸ§¾ RÃ©sumÃ© de session sauvegardÃ© : {json_path}")
    log.debug(f"ðŸ“„ Markdown gÃ©nÃ©rÃ© : {md_path}")
