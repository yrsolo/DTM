from __future__ import annotations

from types import SimpleNamespace
import unittest

from src.contexts.reminders.module import get_module


def _ctx(models: dict[str, str]):
    return SimpleNamespace(cfg=SimpleNamespace(llm=SimpleNamespace(models=models)))


class ReminderModelSelectionTestCase(unittest.TestCase):
    def test_morning_uses_mode_specific_openai_model(self) -> None:
        model = get_module().llm_model_for_mode(
            _ctx({"openai_default": "gpt-4o", "openai_by_mode": {"morning": "gpt-5.5"}}),
            "morning",
        )

        self.assertEqual(model, "gpt-5.5")

    def test_morning_falls_back_to_default_model(self) -> None:
        model = get_module().llm_model_for_mode(_ctx({"openai_default": "gpt-4o"}), "morning")

        self.assertEqual(model, "gpt-4o")

    def test_non_morning_uses_default_model(self) -> None:
        model = get_module().llm_model_for_mode(
            _ctx({"openai_default": "gpt-4o", "openai_by_mode": {"morning": "gpt-5.5"}}),
            "test",
        )

        self.assertEqual(model, "gpt-4o")

    def test_malformed_mode_map_uses_default_model(self) -> None:
        model = get_module().llm_model_for_mode(
            _ctx({"openai_default": "gpt-4o", "openai_by_mode": "morning:gpt-5.5"}),
            "morning",
        )

        self.assertEqual(model, "gpt-4o")


if __name__ == "__main__":
    unittest.main()
