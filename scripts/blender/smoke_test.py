import sys, os, addon_utils

ADDON = "ares"
sys.path.insert(0, os.getcwd())  # repo root

def main():
    try:
        addon_utils.enable(ADDON, default_set=False, persistent=True, handle_error=True)
    except Exception:
        pass

    from ares.core.intent_parser import parse_intent
    from ares.tools.intent_executor import execute_intent

    it = parse_intent("change en rouge")
    if not it:
        raise SystemExit("No intent parsed")
    res = execute_intent(it, auto_fix=True, retries=1)
    print("[SMOKE]", res)
    if not res.get("ok"):
        raise SystemExit("Smoke failed")

if __name__ == "__main__":
    main()
