# -*- coding: utf-8 -*-
"""Static tests ensuring runtime code has no forbidden public endpoints."""

from pathlib import Path

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNoExternalRuntimeRefs(TransactionCase):
    """Scan runtime files for public endpoint references."""

    FORBIDDEN = (
        "stun1.l.google.com",
        "stun2.l.google.com",
        "cdn.jsdelivr.net",
        "tenor.googleapis.com",
        "translation.googleapis.com",
        "api.twilio.com",
    )
    ALLOWED_PARTS = (
        "README",
        "VERSION_HISTORY",
        "tests/",
        "scripts/",
        "test_",
        "intranet_rtc_policy.py",
        "intranet_rtc_diagnostic.py",
    )

    def test_no_forbidden_runtime_references(self):
        """Fail if forbidden public endpoints appear in runtime code."""
        module_path = Path(get_module_path("intranet_mail_rtc_ot"))
        hits = []
        for path in module_path.rglob("*"):
            if not path.is_file() or path.suffix.lower() in {".png", ".wasm", ".tflite", ".binarypb"}:
                continue
            rel = path.relative_to(module_path).as_posix()
            if any(part in rel for part in self.ALLOWED_PARTS):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in self.FORBIDDEN:
                if token in content:
                    hits.append(f"{rel}: {token}")
        self.assertFalse(hits, "Forbidden runtime references found: %s" % hits)
