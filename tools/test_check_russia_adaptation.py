import tempfile
import unittest
from pathlib import Path

from tools.check_russia_adaptation import (
    REQUIRED_RUSSIAN_FIELDS,
    card_requires_freshness,
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
                (book / f"{number:02d}-section.md").write_text("# x\n", encoding="utf-8")
            self.assertEqual(len(list_section_files(root)), 31)

    def test_required_fields_are_russian_user_visible_fields(self):
        self.assertEqual(
            REQUIRED_RUSSIAN_FIELDS,
            ("Стоимость", "Простыми словами", "Польза", "Доказательность", "Источник"),
        )

    def test_validates_complete_russian_card(self):
        card = """### 1. Сделайте действие
<!-- 成本标签: 钱=0 时间=少 毅力=否 收益=大 口径=金钱 -->
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
<!-- 成本标签: 钱=0 时间=少 毅力=否 收益=大 口径=金钱 -->
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
<!-- 成本标签: 钱=0 时间=少 毅力=否 收益=大 口径=死亡率 -->
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

    def test_accepts_upstream_hidden_cost_tag_values(self):
        tag = "<!-- 成本标签: 钱=0 时间=中 毅力=些 收益=大 口径=金钱 -->"
        self.assertEqual(validate_cost_tag(tag), [])

    def test_rejects_translated_hidden_cost_tag_values(self):
        tag = "<!-- 成本标签: 钱=0 时间=средний 毅力=нет 收益=большая 口径=деньги -->"
        errors = validate_cost_tag(tag)
        self.assertTrue(errors)

    def test_reports_forbidden_chinese_government_domains(self):
        text = "Источник: https://www.gov.cn/example и https://cbr.ru/example"
        refs = find_forbidden_china_refs(text)
        self.assertEqual(refs, ["gov.cn"])

    def test_parses_manifest_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "RUSSIA-MIGRATION.md").write_text(
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

    def test_static_ui_is_russian_and_migration_aware(self):
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="ru">', html)
        self.assertIn("HowToLiveBetter-Russia", html)
        self.assertIn("RUSSIA-MIGRATION.md", html)
        self.assertIn("Адаптировано для России", html)
        self.assertIn("Поиск по проверенным рекомендациям", html)
        self.assertIn("<b>31 / 31</b> разделов адаптировано", html)
        self.assertNotIn("Остальные разделы пока сохраняют исходную китайскую редакцию", html)
        self.assertNotIn("高性价比人生指南", html)


if __name__ == "__main__":
    unittest.main()
