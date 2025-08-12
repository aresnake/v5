import glob
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTENTS_DIR = ROOT / "ares" / "config" / "intents"
OUT_DIR = ROOT / "ares" / "config"


def load_all(lang: str):
    lst = []
    for f in sorted(glob.glob(str(INTENTS_DIR / lang / "*.yaml"))):
        with open(f, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or []
            if isinstance(data, dict):
                data = [data]
            lst.extend(data)
    return lst


def norm_phrases(x):
    ph = (x.get("phrases") or []) + ([x.get("phrase")] if x.get("phrase") else [])
    # tri + dédup
    seen, out = set(), []
    for p in ph:
        if isinstance(p, str):
            p2 = p.strip()
            if p2 and p2.lower() not in seen:
                seen.add(p2.lower())
                out.append(p2)
    x.pop("phrase", None)
    x["phrases"] = out
    return x


def sort_intents(intents):
    return sorted(intents, key=lambda d: (d.get("category", "zzz"), d.get("name", "zzz")))


def write_yaml(path: Path, data):
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)
    print(f"[GEN] wrote {path}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INTENTS_DIR.exists():
        print(f"[WARN] No intents dir {INTENTS_DIR}")
        return

    langs = [p.name for p in INTENTS_DIR.iterdir() if p.is_dir()]
    if not langs:
        print("[WARN] No language subfolders in intents/")
        return

    default_written = False
    for lang in langs:
        intents = [norm_phrases(x) for x in load_all(lang)]
        intents = sort_intents(intents)
        out = OUT_DIR / f"voice_config_{lang}.yaml"
        write_yaml(out, intents)
        if lang == "fr":
            write_yaml(OUT_DIR / "voice_config.yaml", intents)
            default_written = True

    if not default_written and langs:
        # fallback: 1ère langue trouvée devient défaut
        first = langs[0]
        data = (OUT_DIR / f"voice_config_{first}.yaml").read_text(encoding="utf-8")
        (OUT_DIR / "voice_config.yaml").write_text(data, encoding="utf-8")
        print(f"[GEN] default voice_config.yaml -> {first}")


if __name__ == "__main__":
    main()
