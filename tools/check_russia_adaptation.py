#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_RUSSIAN_FIELDS = (
    "Стоимость",
    "Простыми словами",
    "Польза",
    "Доказательность",
    "Источник",
)

FORBIDDEN_CHINA_GOVERNMENT_DOMAINS = (
    "gov.cn",
    "nhc.gov.cn",
    "chinacdc.cn",
    "stats.gov.cn",
    "mohrss.gov.cn",
    "samr.gov.cn",
    "mps.gov.cn",
    "mem.gov.cn",
)

SECTION_RE = re.compile(r"^(\d{2})-.*\.md$")
MANIFEST_RE = re.compile(r"^\|\s*(\d{2})\s*\|\s*(not-started|in-progress|complete)\s*\|", re.MULTILINE)
CARD_RE = re.compile(r"(?ms)^###\s+.+?(?=^###\s+|\Z)")
URL_RE = re.compile(r"https?://[^\s)>\]}]+")
COST_TAG_RE = re.compile(
    r"<!--\s*成本标签:\s*"
    r"钱=(?:0|少|多)\s+"
    r"时间=(?:少|中|多)\s+"
    r"毅力=(?:否|些|是)\s+"
    r"收益=(?:大|中|小)\s+"
    r"口径=(?:死亡率|金钱|时间|自由)\s*-->"
)
FRESHNESS_MARKER = "Актуальность РФ проверена:"


def list_section_files(root: Path) -> list[Path]:
    book = root / "book"
    if not book.exists():
        return []
    sections = [path for path in book.glob("*.md") if SECTION_RE.match(path.name)]
    return sorted(sections, key=lambda path: int(SECTION_RE.match(path.name).group(1)))


def parse_migration_manifest(root: Path) -> dict[int, str]:
    path = root / "docs" / "RUSSIA-MIGRATION.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    return {int(number): status for number, status in MANIFEST_RE.findall(text)}


def validate_cost_tag(text: str) -> list[str]:
    if COST_TAG_RE.search(text):
        return []
    return [
        "нет корректного скрытого cost-тега; используйте исходные значения "
        "钱=0|少|多 时间=少|中|多 毅力=否|些|是 收益=大|中|小 "
        "口径=死亡率|金钱|时间|自由"
    ]


def validate_russian_card(card: str, *, require_freshness: bool) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_cost_tag(card))
    for field in REQUIRED_RUSSIAN_FIELDS:
        if not re.search(rf"(?m)^-\s*{re.escape(field)}\s*:", card):
            errors.append(f"нет обязательного поля: {field}")
    match = re.search(r"(?m)^-\s*Доказательность\s*:\s*([^\s]+)", card)
    if match and match.group(1) not in {"A", "B", "C"}:
        errors.append("Доказательность должна быть A, B или C")
    if require_freshness and FRESHNESS_MARKER not in card:
        errors.append(f"нет маркера `{FRESHNESS_MARKER} DD.MM.YYYY.`")
    return errors


def find_forbidden_china_refs(text: str) -> list[str]:
    found: set[str] = set()
    for raw_url in URL_RE.findall(text):
        host = (urlparse(raw_url).hostname or "").lower()
        for forbidden in FORBIDDEN_CHINA_GOVERNMENT_DOMAINS:
            if host == forbidden or host.endswith("." + forbidden):
                found.add(forbidden)
    return sorted(found)


def split_cards(text: str) -> list[str]:
    return CARD_RE.findall(text)


def check_repository(root: Path) -> list[str]:
    errors: list[str] = []
    sections = list_section_files(root)
    if len(sections) != 31:
        errors.append(f"ожидалось 31 файлов book/NN-*.md, найдено {len(sections)}")

    by_number = {
        int(SECTION_RE.match(path.name).group(1)): path
        for path in sections
        if SECTION_RE.match(path.name)
    }
    if len(by_number) != len(sections):
        errors.append("обнаружены дублирующиеся номера разделов book/NN-*.md")

    for number in (1, 5, 7, 8, 9, 19, 24):
        if number not in by_number:
            errors.append(f"отсутствует целевой раздел {number:02d}")

    statuses = parse_migration_manifest(root)
    if len(statuses) != 31:
        errors.append(f"в RUSSIA-MIGRATION.md должно быть 31 статусов, найдено {len(statuses)}")

    for number, status in sorted(statuses.items()):
        if status != "complete":
            continue
        path = by_number.get(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8")
        forbidden = find_forbidden_china_refs(text)
        if forbidden:
            errors.append(f"{path}: китайские госдомены в complete-разделе: {', '.join(forbidden)}")
        cards = split_cards(text)
        if not cards:
            errors.append(f"{path}: не найдено карточек `### ...`")
        for index, card in enumerate(cards, start=1):
            for error in validate_russian_card(card, require_freshness=True):
                errors.append(f"{path}: карточка {index}: {error}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = check_repository(root)
    if errors:
        print("Russia adaptation check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Russia adaptation check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())