import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "locales"
with open(BASE / "uz.json", encoding="utf-8") as f: UZ = json.load(f)
with open(BASE / "ru.json", encoding="utf-8") as f: RU = json.load(f)

def t(lang: str, key: str, **kwargs):
    text = (UZ if lang == "uz" else RU).get(key, key)
    return text.format(**kwargs)
