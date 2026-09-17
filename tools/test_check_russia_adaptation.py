import tempfile
import unittest
from pathlib import Path

from tools.check_russia_adaptation import (
    REQUIRED_RUSSIAN_FIELDS,
    card_requires_freshness,
    contains_cjk,
    find_cjk_paths,
    find_forbidden_china_refs,
    list_section_files,
    parse_migration_manifest,
    parse_readme_section_links,
    validate_cost_tag,
    validate_russian_card,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RussiaAdaptationChecksTest(unittest.TestCase):
    def test_lists_exactly_31_numbered_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = root / "book"
            book.mkdir()
            for number in range(1, 32):
                (book / f"{number:02d}-раздел.md").write_text("# x\n", encoding="utf-8")
            self.assertEqual(len(list_section_files(root)), 31)

    def test_required_fields_are_russian_user_visible_fields(self):
        self.assertEqual(
            REQUIRED_RUSSIAN_FIELDS,
            ("Стоимость", "Простыми словами", "Польза", "Доказательность", "Источник"),
        )

    def test_accepts_russian_metadata_tag(self):
        tag = (
            "<!-- метаданные: деньги=0 время=средне усилие=немного "
            "польза=высокая метрика=деньги -->"
        )
        self.assertEqual(validate_cost_tag(tag), [])

    def test_rejects_invalid_metadata_tag(self):
        tag = (
            "<!-- метаданные: деньги=0 время=средний усилие=нет "
            "польза=большая метрика=деньги -->"
        )
        self.assertTrue(validate_cost_tag(tag))

    def test_validates_complete_russian_card(self):
        card = """### 1. Сделайте действие
<!-- метаданные: деньги=0 время=мало усилие=нет польза=высокая метрика=деньги -->
- Стоимость: 0 ₽
- Простыми словами: Практический вывод.
- Польза: Конкретный эффект.
- Доказательность: A
- Источник: https://cbr.ru/
- Примечание: Актуальность РФ проверена: 17.09.2026.
"""
        self.assertEqual(validate_russian_card(card, require_freshness=True), [])

    def test_russian_source_requires_freshness(self):
        card = """### 1. Сделайте действие
<!-- метаданные: деньги=0 время=мало усилие=нет польза=высокая метрика=деньги -->
- Стоимость: 0 ₽
- Простыми словами: Вывод.
- Польза: Эффект.
- Доказательность: B
- Источник: https://gosuslugi.ru/
"""
        self.assertTrue(card_requires_freshness(card))
        errors = validate_russian_card(card, require_freshness=card_requires_freshness(card))
        self.assertTrue(any("Актуальность РФ проверена" in error for error in errors))

    def test_international_source_does_not_require_russian_freshness(self):
        card = """### 1. Сделайте действие
<!-- метаданные: деньги=0 время=мало усилие=нет польза=высокая метрика=здоровье -->
- Стоимость: 0 ₽
- Простыми словами: Вывод.
- Польза: Эффект.
- Доказательность: A
- Источник: https://www.who.int/example
"""
        self.assertFalse(card_requires_freshness(card))
        self.assertEqual(
            validate_russian_card(card, require_freshness=card_requires_freshness(card)), []
        )

    def test_reports_forbidden_chinese_government_domains(self):
        text = "Источник: https://www.gov.cn/example и https://cbr.ru/example"
        refs = find_forbidden_china_refs(text)
        self.assertEqual(refs, ["gov.cn"])

    def test_contains_cjk_uses_unicode_range(self):
        self.assertTrue(contains_cjk("\u4e00"))
        self.assertFalse(contains_cjk("Русский текст и English text"))

    def test_finds_cjk_in_active_text_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "book").mkdir()
            (root / "book" / "01-тест.md").write_text("\u4e00", encoding="utf-8")
            (root / "LICENSE").write_text("\u4e00", encoding="utf-8")
            paths = find_cjk_paths(root)
            self.assertEqual([path.relative_to(root).as_posix() for path in paths], ["book/01-тест.md"])

    def test_parses_manifest_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "СТАТУС-АДАПТАЦИИ.md").write_text(
                "| 01 | in-progress |\n| 05 | complete |\n", encoding="utf-8"
            )
            statuses = parse_migration_manifest(root)
            self.assertEqual(statuses[1], "in-progress")
            self.assertEqual(statuses[5], "complete")

    def test_readme_has_31_existing_section_links(self):
        links = parse_readme_section_links(PROJECT_ROOT)
        self.assertEqual(len(links), 31)
        for number, relative_path in links.items():
            self.assertTrue(
                (PROJECT_ROOT / relative_path).exists(),
                f"README section {number:02d} points to missing {relative_path}",
            )
            self.assertFalse(contains_cjk(relative_path))

    def test_static_ui_is_fully_russian(self):
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="ru">', html)
        self.assertIn("HowToLiveBetter-Russia", html)
        self.assertIn("СТАТУС-АДАПТАЦИИ.md", html)
        self.assertIn("Адаптировано для России", html)
        self.assertIn("Поиск по проверенным рекомендациям", html)
        self.assertIn("<b>31 / 31</b> разделов адаптировано", html)
        self.assertFalse(contains_cjk(html))

    def test_repository_has_no_cjk_in_active_text_files(self):
        self.assertEqual(find_cjk_paths(PROJECT_ROOT), [])


if __name__ == "__main__":
    unittest.main()
