from __future__ import annotations

import unittest

from src.services.attachments.policy import build_attachment_capabilities, infer_attachment_kind


class AttachmentPolicyTestCase(unittest.TestCase):
    def test_infer_attachment_kind_supports_pdf(self) -> None:
        self.assertEqual(infer_attachment_kind("application/pdf"), "pdf")
        self.assertEqual(
            build_attachment_capabilities("pdf"),
            ["browser_view", "download", "pdf_view"],
        )

    def test_infer_attachment_kind_supports_legacy_doc(self) -> None:
        self.assertEqual(infer_attachment_kind("application/msword"), "doc")
        self.assertEqual(
            build_attachment_capabilities("doc"),
            ["browser_view", "download", "pdf_preview"],
        )


if __name__ == "__main__":
    unittest.main()
