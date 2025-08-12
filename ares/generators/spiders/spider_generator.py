import os
import random

import yaml

from ares.core.logger import get_logger

log = get_logger("SpiderGen")

BASE_PATH = os.path.dirname(__file__)


def _load_yaml(name: str) -> dict:
    with open(os.path.join(BASE_PATH, name), encoding="utf-8") as f:
        return yaml.safe_load(f)


_species = _load_yaml("species_manifest.yaml")["species"]
_styles = _load_yaml("styles_manifest.yaml")["styles"]


def list_species() -> dict[str, dict]:
    return _species


def list_styles() -> dict[str, dict]:
    return _styles


def _get_manager():
    try:
        from ares.tools.text2mesh_manager import get_manager

        return get_manager()
    except Exception as e:
        log.error(f"Text2Mesh manager indisponible: {e}")
        return None


def generate_spider(
    species_key: str, style_key: str | None = None, provider: str = "offline_stub"
) -> str:
    if species_key not in _species:
        raise ValueError(f"Unknown species: {species_key}")
    species = _species[species_key]
    style = _styles[style_key or species["default_style"]]
    prompt = f"{species['common_name']} ({species['scientific_name']}), {style['description']}, full body, high detail"
    options = {
        "camera_fov": style.get("camera_fov", 35),
        "lighting": style.get("lighting", ""),
        "texture_resolution": style.get("texture_resolution", "2K"),
    }
    mng = _get_manager()
    if not mng:
        raise RuntimeError("Text2Mesh manager not available.")
    return mng.submit(provider, prompt, options)


def generate_random_spider(provider: str = "offline_stub") -> str:
    sp = random.choice(list(_species.keys()))
    st = random.choice(list(_styles.keys()))
    return generate_spider(sp, st, provider)
