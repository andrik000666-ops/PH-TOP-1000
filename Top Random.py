import json
import random
import re
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "исходники"
RESULTS = BASE / "Результаты"
HISTORY = RESULTS / "used_models.json"
OUTPUT = RESULTS / "Мои результаты.txt"


def normalize_name(value):
    """Сравнивает псевдонимы без учёта регистра, пробелов и знаков."""
    return re.sub(r"[^a-zа-яё0-9]", "", value.casefold())


def load_models():
    files = [p for p in SOURCE.iterdir()
             if p.is_file() and p.stem.casefold() == "pornhub - top 1000"]

    if not files:
        raise FileNotFoundError("Не найден файл PornHub - TOP 1000.")

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

    if len(models) != 1000 or {m["id"] for m in models} != set(range(1, 1001)):
        raise ValueError("В файле должно быть 1000 моделей с ID от 1 до 1000.")

    return models


def save_history(ids):
    RESULTS.mkdir(exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=str(RESULTS))

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"used_ids": sorted(ids)}, f)
        os.replace(temp, HISTORY)
    except:
        if os.path.exists(temp):
            os.remove(temp)
        raise


def main():
    RESULTS.mkdir(exist_ok=True)
    models = load_models()

    ids = set()
    if HISTORY.exists():
        ids = set(json.loads(HISTORY.read_text(encoding="utf-8")).get("used_ids", []))

    print()
    print("♡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━♡")
    print("          ДОПОЛНЕНИЕ ИТОГОВ")
    print("♡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━♡")
    print("  Если хотите дополнить итоги,")
    print("  введите номер актрисы от 1 до 1000")
    print("  или её псевдоним (1–2 слова).")
    print("  Для случайного выбора просто нажмите Enter.")
    print("♡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━♡")

    while True:
        print()
        selection = input("Ваш выбор: ").strip()

        if selection == "":
            available = [m for m in models if m["id"] not in ids]
            if not available:
                print("Все модели использованы.")
                return
            model = random.SystemRandom().choice(available)
            break

        if selection.isdigit():
            number = int(selection)
            if 1 <= number <= 1000:
                model = next(m for m in models if m["id"] == number)
                break
            print("Ошибка: номер должен быть от 1 до 1000.")
            continue

        normalized_selection = normalize_name(selection)
        matches = [
            m for m in models
            if normalize_name(m["name"]) == normalized_selection
        ]

        if len(matches) == 1:
            model = matches[0]
            break

        if len(matches) > 1:
            print("Найдено несколько совпадений. Уточните псевдоним или введите номер:")
            for candidate in matches:
                print(f"  №{candidate['id']} — {candidate['name']}")
            continue

        from difflib import SequenceMatcher
        suggestions = []
        for candidate in models:
            score = SequenceMatcher(
                None, normalized_selection, normalize_name(candidate["name"])
            ).ratio()
            if score >= 0.78:
                suggestions.append((score, candidate))

        suggestions.sort(key=lambda item: item[0], reverse=True)
        if suggestions:
            print("Точное совпадение не найдено. Возможно, вы имели в виду:")
            for _, candidate in suggestions[:5]:
                print(f"  №{candidate['id']} — {candidate['name']}")
            print("Введите точный псевдоним или номер из списка.")
        else:
            print("Ошибка: актриса с таким псевдонимом не найдена.")
            print("Проверьте написание, введите номер от 1 до 1000 или нажмите Enter.")

    ids.add(model["id"])
    save_history(ids)

    print()
    print("♡━━━━━━━━━━━━━━━━━━━━♡")
    print(f"  ♡  {model['name']}")
    print(f"  ♡  Видео: {model['videos']}")
    print(f"  ♡  Просмотры: {model['views']}")
    print(f"  ♡  Место: {model['rank']}")
    print("♡━━━━━━━━━━━━━━━━━━━━♡")
    print()

    while True:
        rating = input("Оценка (1–20): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 20:
            break

    while True:
        duration = input("Время (м.сс): ").strip()
        if re.fullmatch(r"\d+\.\d{1,2}", duration):
            minutes, seconds = map(int, duration.split("."))
            if seconds <= 59:
                break

    while True:
        comment = input("Комментарий: ").strip()
        if len(comment.split()) <= 5:
            break

    date = datetime.now(
        timezone(timedelta(hours=3))
    ).strftime("%d.%m.%Y %H:%M")

    entry = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"♡  {date}\n"
        f"♡  {model['name']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Место в рейтинге: {model['rank']}\n"
        f"Просмотры: {model['views']}\n"
        f"Оценка: {rating}/20\n"
        f"Время: {duration}\n"
        "\n"
        "Комментарий:\n"
        f"{comment if comment else '—'}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    with OUTPUT.open("a", encoding="utf-8") as f:
        f.write(entry)

    print()
    print("♡ ГОТОВО! Запись успешно сохранена. ♡")


try:
    main()
except KeyboardInterrupt:
    print("\nОтменено.")
except Exception as e:
    print("\nОшибка:", e)