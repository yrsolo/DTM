from __future__ import annotations

import importlib
import unittest


class TargetSkeletonImportsTestCase(unittest.TestCase):
    def test_target_entrypoint_handler_imports(self) -> None:
        module = importlib.import_module("src.entrypoints.root.handler")
        self.assertTrue(hasattr(module, "handle"))

    def test_target_platform_runtime_imports(self) -> None:
        module = importlib.import_module("src.platform.runtime.queue_dispatch")
        self.assertTrue(hasattr(module, "dispatch_command"))

    def test_target_context_public_facades_import(self) -> None:
        module_names = [
            "src.contexts.attachments.public",
            "src.contexts.reminders.public",
            "src.contexts.snapshot.public",
            "src.contexts.rendering.public",
            "src.contexts.telegram_interaction.public",
            "src.contexts.access_api.public",
        ]
        for module_name in module_names:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertTrue(hasattr(module, "get_public_api"))


if __name__ == "__main__":
    unittest.main()
