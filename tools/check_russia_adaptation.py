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

TEXT_EXTENSIONS = {".md", ".html", ".py", ".yml", ".yaml", ".xml", ".txt", ".json", ".css", ".js"}
SECTION_RE = re.compile(r"^(\d{2})-.*\.md$")
MANIFEST_RE = re.compile(r"^\|\s*(\d{2})\s*\|\s*(not-started|in-progress|complete)\s*\|", re.MULTILINE)
README_SECTION_RE = re.compile(r"^\|\s*(\d{1,2})\s*\|\s*\[[^\]]+\]\((book/[^)]+\.md)\)\s*\|", re.MULTILINE)
CARD_RE = re.compile(r"(?ms)^###\s+.+?(?=^###\s+|\Z)")
URL_RE = re.compile(r"https?://[^\s)>\]}]+")
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
COST_TAG_RE = re.compile(
    r"<!--\s*метаданные:\s*"
    r"деньги=(?:0|мало|много)\s+"
    r"время=(?:мало|средне|много)\s+"
    r"усилие=(?:нет|немного|да)\s+"
    r"польза=(?:высокая|средняя|низкая)\s+"
    r"метрика=(?:здоровье|деньги|время|свобода)\s*-->"
)
FRESHNESS_MARKER = "Актуальность РФ проверена:"


def contains_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def find_cjk_paths(root: Path) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts or relative.as_posix() == "LICENSE":
            continue
        if contains_cjk(relative.as_posix()):
            found.append(path)
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if contains_cjk(text):
            found.append(path)
    return sorted(found, key=lambda item: item.relative_to(root).as_posix())


def list_section_files(root: Path) -> list[Path]:
    book = root / "book"
    if not book.exists():
        return []
    sections = [path for path in book.glob("*.md") if SECTION_RE.match(path.name)]
    return sorted(sections, key=lambda path: int(SECTION_RE.match(path.name).group(1)))


def parse_migration_manifest(root: Path) -> dict[int, str]:
    path = root / "docs" / "СТАТУС-АДАПТАЦИИ.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    return {int(number): status for number, status in MANIFEST_RE.findall(text)}


def parse_readme_section_links(root: Path) -> dict[int, str]:
    path = root / "README.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    return {int(number): relative_path for number, relative_path in README_SECTION_RE.findall(text)}


def validate_cost_tag(text: str) -> list[str]:
    if COST_TAG_RE.search(text):
        return []
    return [
        "нет корректного скрытого тега метаданных; используйте значения "
        "деньги=0|мало|много время=мало|средне|много усилие=нет|немного|да "
        "польза=высокая|средняя|низкая метрика=здоровье|деньги|время|свобода"
    ]


def card_requires_freshness(card: str) -> bool:
    """Return True when a card relies on Russia-specific sources or rules."""
    for raw_url in URL_RE.findall(card):
        host = (urlparse(raw_url).hostname or "").lower()
        if host == "ru" or host.endswith(".ru"):
            return True
    return False


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

    readme_links = parse_readme_section_links(root)
    if len(readme_links) != 31:
        errors.append(f"в README должно быть 31 ссылок на разделы, найдено {len(readme_links)}")
    for number, relative_path in sorted(readme_links.items()):
        target = root / relative_path
        if not target.exists():
            errors.append(f"README: раздел {number:02d} ссылается на отсутствующий файл {relative_path}")
            continue
        match = SECTION_RE.match(target.name)
        if not match or int(match.group(1)) != number:
            errors.append(f"README: номер {number:02d} не совпадает с файлом {relative_path}")
        if contains_cjk(relative_path):
            errors.append(f"README: путь раздела {number:02d} содержит CJK")

    statuses = parse_migration_manifest(root)
    if len(statuses) != 31:
        errors.append(f"в СТАТУС-АДАПТАЦИИ.md должно быть 31 статусов, найдено {len(statuses)}")

    for number, status in sorted(statuses.items()):
        if status != "complete":
            continue
        path = by_number.get(number)
        if path is None:
            errors.append(f"complete-раздел {number:02d} отсутствует в book/")
            continue
        text = path.read_text(encoding="utf-8")
        forbidden = find_forbidden_china_refs(text)
        if forbidden:
            errors.append(f"{path}: китайские госдомены в complete-разделе: {', '.join(forbidden)}")
        cards = split_cards(text)
        if not cards:
            errors.append(f"{path}: не найдено карточек `### ...`")
        for index, card in enumerate(cards, start=1):
            for error in validate_russian_card(
                card,
                require_freshness=card_requires_freshness(card),
            ):
                errors.append(f"{path}: карточка {index}: {error}")

    cjk_paths = find_cjk_paths(root)
    for path in cjk_paths:
        errors.append(f"обнаружен CJK в активном файле: {path.relative_to(root).as_posix()}")

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
