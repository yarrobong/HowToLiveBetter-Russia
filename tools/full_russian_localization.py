#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
DOCS = ROOT / "docs"

NAMES = {
    1: "01-безопасность-и-профилактика.md",
    2: "02-здоровье-и-долголетие.md",
    3: "03-энергия-и-восстановление.md",
    4: "04-время-и-продуктивность.md",
    5: "05-деньги-и-защита-от-мошенников.md",
    6: "06-сомнительные-покупки-и-практики.md",
    7: "07-когда-денег-почти-нет.md",
    8: "08-правовая-и-имущественная-безопасность.md",
    9: "09-юридические-красные-линии.md",
    10: "10-отношения-брак-и-имущество.md",
    11: "11-риски-разработчика-и-техспециалиста.md",
    12: "12-бизнес-и-личные-деньги.md",
    13: "13-экстренные-ситуации.md",
    14: "14-аккаунты-и-информационная-безопасность.md",
    15: "15-аренда-и-покупка-жилья.md",
    16: "16-жизнь-с-хроническим-заболеванием.md",
    17: "17-пожилые-родственники.md",
    18: "18-дети-расходы-время-и-решения.md",
    19: "19-работа-увольнение-и-производственные-травмы.md",
    20: "20-новорожденный-ребенок.md",
    21: "21-поездки-за-границу-и-безопасность.md",
    22: "22-отдых-и-восстановление.md",
    23: "23-навыки-которые-выгодно-изучать.md",
    24: "24-медицинская-помощь.md",
    25: "25-после-смерти-близкого.md",
    26: "26-сайт-сервис-или-интернет-платформа.md",
    27: "27-беременность-и-роды.md",
    28: "28-здоровье-и-внешность.md",
    29: "29-после-тяжелого-жизненного-события.md",
    30: "30-здоровье-ребенка-школьного-возраста.md",
    31: "31-пути-после-18-лет.md",
}

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

LABEL = "\u6210\u672c\u6807\u7b7e"
MONEY = "\u94b1"
TIME = "\u65f6\u95f4"
EFFORT = "\u6bc5\u529b"
BENEFIT = "\u6536\u76ca"
METRIC = "\u53e3\u5f84"
LOW = "\u5c11"
HIGH = "\u591a"
MID = "\u4e2d"
NO = "\u5426"
SOME = "\u4e9b"
YES = "\u662f"
BIG = "\u5927"
SMALL = "\u5c0f"
DEATH = "\u6b7b\u4ea1\u7387"
CASH = "\u91d1\u94b1"
FREEDOM = "\u81ea\u7531"

OLD_TAG_RE = re.compile(
    rf"<!--\s*{LABEL}:\s*"
    rf"{MONEY}=(0|{LOW}|{HIGH})\s+"
    rf"{TIME}=({LOW}|{MID}|{HIGH})\s+"
    rf"{EFFORT}=({NO}|{SOME}|{YES})\s+"
    rf"{BENEFIT}=({BIG}|{MID}|{SMALL})\s+"
    rf"{METRIC}=({DEATH}|{CASH}|{TIME}|{FREEDOM})\s*-->"
)

MONEY_MAP = {"0": "0", LOW: "мало", HIGH: "много"}
TIME_MAP = {LOW: "мало", MID: "средне", HIGH: "много"}
EFFORT_MAP = {NO: "нет", SOME: "немного", YES: "да"}
BENEFIT_MAP = {BIG: "высокая", MID: "средняя", SMALL: "низкая"}
METRIC_MAP = {DEATH: "здоровье", CASH: "деньги", TIME: "время", FREEDOM: "свобода"}

TEXT_EXTENSIONS = {".md", ".html", ".py", ".yml", ".yaml", ".xml", ".txt", ".json", ".css", ".js"}


def new_tag(match: re.Match[str]) -> str:
    money, time, effort, benefit, metric = match.groups()
    return (
        "<!-- метаданные: "
        f"деньги={MONEY_MAP[money]} "
        f"время={TIME_MAP[time]} "
        f"усилие={EFFORT_MAP[effort]} "
        f"польза={BENEFIT_MAP[benefit]} "
        f"метрика={METRIC_MAP[metric]} -->"
    )


def rename_books() -> dict[str, str]:
    replacements: dict[str, str] = {}
    for number, new_name in NAMES.items():
        matches = list(BOOK.glob(f"{number:02d}-*.md"))
        if len(matches) != 1:
            raise RuntimeError(f"Раздел {number:02d}: ожидался один файл, найдено {len(matches)}")
        old = matches[0]
        text = old.read_text(encoding="utf-8")
        text, count = OLD_TAG_RE.subn(new_tag, text)
        if count == 0:
            raise RuntimeError(f"Раздел {number:02d}: не найдено ни одного старого тега")
        new = BOOK / new_name
        new.write_text(text, encoding="utf-8")
        if old != new:
            old.unlink()
        replacements[f"book/{old.name}"] = f"book/{new_name}"
    return replacements


def rename_main_docs() -> dict[str, str]:
    pairs = {
        DOCS / "СТАТУС-АДАПТАЦИИ.md": DOCS / "СТАТУС-АДАПТАЦИИ.md",
        DOCS / "ИСТОЧНИКИ-РФ.md": DOCS / "ИСТОЧНИКИ-РФ.md",
    }
    replacements: dict[str, str] = {}
    for old, new in pairs.items():
        if old.exists():
            old.rename(new)
        replacements[old.relative_to(ROOT).as_posix()] = new.relative_to(ROOT).as_posix()
        replacements[old.name] = new.name
    return replacements


def replace_references(replacements: dict[str, str]) -> None:
    replacements = dict(replacements)
    replacements[
        "docs/superpowers/specs/2026-09-17-полная-русификация.md"
    ] = "docs/superpowers/specs/2026-09-17-полная-русификация.md"
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def rewrite_claude() -> None:
    content = """# Правила проекта HowToLiveBetter-Russia

Этот репозиторий — российская редакция доказательного практического справочника. Рабочий язык проекта — русский.

## Формат разделов

- В `book/` должно быть ровно 31 файла `NN-*.md`.
- Имя каждого файла и весь пользовательский текст должны быть на русском языке.
- Каждый раздел начинается ссылкой на `README.md`, затем заголовком раздела.
- Каждая рекомендация начинается заголовком `###` и содержит поля `Стоимость`, `Простыми словами`, `Польза`, `Доказательность`, `Источник`.

## Скрытые метаданные

После заголовка карточки используется только такой формат:

`<!-- метаданные: деньги=0|мало|много время=мало|средне|много усилие=нет|немного|да польза=высокая|средняя|низкая метрика=здоровье|деньги|время|свобода -->`

Старые форматы метаданных запрещены.

## Источники

- Для российских законов, процедур, выплат, налогов и административных правил приоритет имеют официальные российские первоисточники.
- Для универсальных медицинских и поведенческих рекомендаций используются систематические обзоры, метаанализы, крупные исследования и международные профильные организации.
- Не придумывать цифры, сроки, штрафы и DOI по памяти.
- Для российских норм указывать `Актуальность РФ проверена: DD.MM.YYYY.`.
- Китайские локальные нормы и государственные источники не использовать как основание российской рекомендации.

## Ссылки и навигация

- `README.md` содержит ровно 31 ссылку на файлы `book/`.
- При переименовании файла обновлять все ссылки в README и документации.
- `index.html` читает список разделов из README и должен оставаться совместимым с ним.

## Проверка

Перед merge обязательно выполнить:

```bash
python -m unittest tools.test_check_russia_adaptation -v
python tools/check_russia_adaptation.py
```

Checker контролирует структуру 31 раздела, обязательные поля карточек, русский формат метаданных, даты актуальности российских норм, корректность ссылок и отсутствие китайских иероглифов в активных текстовых файлах.
"""
    (ROOT / "CLAUDE.md").write_text(content, encoding="utf-8")


def remove_legacy() -> None:
    reviews = DOCS / "superpowers" / "reviews"
    if reviews.exists():
        shutil.rmtree(reviews)

    for folder_name in ("plans", "specs"):
        folder = DOCS / "superpowers" / folder_name
        if not folder.exists():
            continue
        for path in folder.iterdir():
            if path.is_file() and "полная-русификация" not in path.name:
                path.unlink()

    for name in ("wave-3-review.md", "wave-3-summary.md"):
        path = DOCS / name
        if path.exists():
            path.unlink()

    for path in sorted(DOCS.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        relative = path.relative_to(ROOT).as_posix()
        if CJK_RE.search(relative):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists():
                path.unlink()

    for relative in ("og.png", "tools/og.html"):
        path = ROOT / relative
        if path.exists():
            path.unlink()


def assert_no_cjk() -> None:
    bad: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if CJK_RE.search(relative):
            bad.append(relative)
            continue
        if relative == "LICENSE" or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8")
        if CJK_RE.search(text):
            bad.append(relative)
    if bad:
        raise RuntimeError("После миграции остались CJK: " + ", ".join(sorted(bad)))


def main() -> None:
    replacements = rename_books()
    replacements.update(rename_main_docs())
    replace_references(replacements)
    rewrite_claude()
    remove_legacy()
    assert_no_cjk()
    print("Полная русификация применена успешно")


if __name__ == "__main__":
    main()
