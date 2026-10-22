from pathlib import Path
import unittest

from update_daily_gif import BASE_URL, animation_for_day, update_readme


class DailyGifTests(unittest.TestCase):
    def test_all_weekdays(self):
        self.assertEqual([animation_for_day(day) for day in range(7)], [1, 2, 3, 4, 5, 5, 5])

    def test_invalid_weekday(self):
        for day in (-1, 7):
            with self.assertRaises(ValueError):
                animation_for_day(day)

    def test_only_marked_region_changes_and_updates_are_idempotent(self):
        original = "before\n<!-- daily-gif:start -->old<!-- daily-gif:end -->\nafter"
        for day in range(7):
            updated = update_readme(original, day)
            self.assertTrue(updated.startswith("before\n"))
            self.assertTrue(updated.endswith("\nafter"))
            self.assertIn(f"{BASE_URL}/{min(day + 1, 5)}.gif", updated)
            self.assertEqual(update_readme(updated, day), updated)

    def test_missing_or_duplicate_markers_fail_safely(self):
        region = "<!-- daily-gif:start -->old<!-- daily-gif:end -->"
        for content in ("", "<!-- daily-gif:start -->", region * 2):
            with self.assertRaises(ValueError):
                update_readme(content, 0)

    def test_actual_readme_has_valid_markers(self):
        readme = Path(__file__).resolve().parents[2] / "README.md"
        update_readme(readme.read_text(encoding="utf-8"), 0)


if __name__ == "__main__":
    unittest.main()
