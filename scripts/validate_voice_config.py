import yaml, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "ares" / "config" / "voice_config.yaml"

ALLOWED_TOP_KEYS = {
    "name","phrases","phrase","operator","params","category","description",
    "op","args","kwargs","direct","requires","ensure","meta",
}

def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or []

def is_context_path(op: str) -> bool:
    return op.startswith(("context.","bpy.context.","data.","bpy.data.")) or "." in op

def validate(items):
    names, errors = set(), []
    for i, it in enumerate(items, 1):
        if not isinstance(it, dict):
            errors.append(f"Item #{i} not a dict")
            continue
        unk = [k for k in it.keys() if k not in ALLOWED_TOP_KEYS]
        if unk:
            errors.append(f"{it.get('name','<no-name>')}: unknown keys {unk}")

        name = it.get("name")
        if not name:
            errors.append(f"Item #{i} missing 'name'")
        elif name in names:
            errors.append(f"Duplicate intent name: {name}")
        else:
            names.add(name)

        phrases = it.get("phrases") or []
        if not phrases:
            errors.append(f"{name}: empty 'phrases'")

        # must have at least one way to execute
        if "operator" in it:
            if not isinstance(it["operator"], str) or not is_context_path(it["operator"]):
                errors.append(f"{name}: invalid operator '{it['operator']}'")
        elif "op" in it or "direct" in it:
            pass
        else:
            errors.append(f"{name}: missing operator/op/direct")

    return errors

def main():
    cfg = CFG
    items = load_yaml(cfg)
    errs = validate(items)
    if errs:
        print("❌ voice_config.yaml invalid:")
        for e in errs: print(" -", e)
        sys.exit(1)
    print("✅ voice_config.yaml OK")

if __name__ == "__main__":
    main()
