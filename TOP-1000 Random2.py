
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "исходники"


def load_models():
    files = [
        p for p in SOURCE.iterdir()
        if p.is_file()
        and p.stem.casefold() == "pornhub - top 1000"
    ]

    if not files:
        raise FileNotFoundError("Не найден PornHub - TOP 1000.")

    models = []

    for line in files[0].read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue

        parts = [x.strip() for x in line.split("|")]

        if len(parts) != 5:
            raise ValueError("Ошибка строки: " + line)

        model_id, name, videos, views, rank = parts

        models.append({
            "id": int(model_id),
            "name": name,
            "videos": int(videos),
            "views": views,
            "rank": int(rank)
        })

    if len(models) != 1000:
        raise ValueError("В файле должно быть 1000 актрис.")

    return models


models = load_models()
model = random.SystemRandom().choice(models)

print()
print("♡━━━━━━━━━━━━━━━━━━━━♡")
print(f"  ♡  {model['name']}")
print(f"  ♡  Видео: {model['videos']}")
print(f"  ♡  Просмотры: {model['views']}")
print(f"  ♡  Место: {model['rank']}")
print("♡━━━━━━━━━━━━━━━━━━━━♡")
