import tempfile
import unittest
from pathlib import Path

from tools.check_russia_adaptation import (
    REQUIRED_RUSSIAN_FIELDS,
    find_forbidden_china_refs,
    list_section_files,
    parse_migration_manifest,
    validate_cost_tag,
    validate_russian_card,
)


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

    def test_reports_missing_freshness_for_russia_specific_card(self):
        card = """### 1. Сделайте действие
- Стоимость: 0 ₽
- Простыми словами: Вывод.
- Польза: Эффект.
- Доказательность: B
- Источник: https://gosuslugi.ru/
"""
        errors = validate_russian_card(card, require_freshness=True)
        self.assertTrue(any("Актуальность РФ проверена" in error for error in errors))

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


if __name__ == "__main__":
    unittest.main()