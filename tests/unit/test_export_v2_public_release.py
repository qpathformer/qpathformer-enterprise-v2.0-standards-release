from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from export_v2_public_release import (  # noqa: E402
    ExportError,
    execute,
    parse_args,
)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class ExportV2PublicReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.source.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_allowlist(self, records: list[dict[str, object]]) -> Path:
        path = self.root / "allowlist.json"
        path.write_text(
            json.dumps(
                {
                    "document_id": "test-allowlist",
                    "source_root_logical": "source",
                    "target_root_logical": "target",
                    "resolved_files": records,
                }
            ),
            encoding="utf-8",
        )
        return path

    def record(self, path: str, content: bytes, policy: str) -> dict[str, object]:
        source_path = self.source.joinpath(*path.split("/"))
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(content)
        return {
            "path": path,
            "source_bytes": len(content),
            "source_sha256": sha256(content),
            "byte_policy": policy,
        }

    def args(self, allowlist: Path, *extra: str):
        return parse_args(
            [
                "--source-root",
                str(self.source),
                "--target-root",
                str(self.target),
                "--allowlist",
                str(allowlist),
                *extra,
            ]
        )

    def test_dry_run_does_not_create_target(self) -> None:
        record = self.record("docs/readme.md", b"line\r\n", "normalize_lf")
        report = execute(self.args(self.write_allowlist([record]), "--dry-run"))
        self.assertEqual(report["mode"], "dry_run")
        self.assertFalse(self.target.exists())

    def test_export_normalizes_active_text_and_preserves_historical_bytes(self) -> None:
        active = self.record("active.txt", b"a\r\nb\r\n", "normalize_lf")
        historical = self.record("history.json", b"{\r\n  \"a\": 1\r\n}\r\n", "preserve")
        report = execute(self.args(self.write_allowlist([active, historical])))
        self.assertEqual(report["mode"], "export")
        self.assertEqual((self.target / "active.txt").read_bytes(), b"a\nb\n")
        self.assertEqual(
            (self.target / "history.json").read_bytes(),
            b"{\r\n  \"a\": 1\r\n}\r\n",
        )

    def test_verify_only_accepts_exact_tree(self) -> None:
        record = self.record("a.json", b"{}\n", "preserve")
        allowlist = self.write_allowlist([record])
        execute(self.args(allowlist))
        report = execute(self.args(allowlist, "--verify-only"))
        self.assertEqual(report["mode"], "verify_only")

    def test_verify_only_rejects_extra_file(self) -> None:
        record = self.record("a.json", b"{}\n", "preserve")
        allowlist = self.write_allowlist([record])
        execute(self.args(allowlist))
        (self.target / "extra.txt").write_text("extra", encoding="utf-8")
        with self.assertRaisesRegex(ExportError, "target_files_unexpected"):
            execute(self.args(allowlist, "--verify-only"))

    def test_source_hash_mismatch_fails_closed(self) -> None:
        record = self.record("a.json", b"{}\n", "preserve")
        record["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ExportError, "source_sha256_mismatch"):
            execute(self.args(self.write_allowlist([record]), "--dry-run"))

    def test_path_traversal_is_rejected(self) -> None:
        record = {
            "path": "../escape.txt",
            "source_bytes": 0,
            "source_sha256": sha256(b""),
            "byte_policy": "preserve",
        }
        with self.assertRaisesRegex(ExportError, "unsafe_allowlist_path_rejected"):
            execute(self.args(self.write_allowlist([record]), "--dry-run"))

    def test_non_empty_target_is_rejected(self) -> None:
        record = self.record("a.json", b"{}\n", "preserve")
        self.target.mkdir()
        (self.target / "existing.txt").write_text("existing", encoding="utf-8")
        with self.assertRaisesRegex(ExportError, "target_not_empty"):
            execute(self.args(self.write_allowlist([record])))

    def test_source_symlink_is_rejected_when_supported(self) -> None:
        real = self.source / "real.txt"
        real.write_text("real", encoding="utf-8")
        link = self.source / "link.txt"
        try:
            os.symlink(real, link)
        except OSError:
            self.skipTest("symlink creation is unavailable")
        record = {
            "path": "link.txt",
            "source_bytes": 4,
            "source_sha256": sha256(b"real"),
            "byte_policy": "preserve",
        }
        with self.assertRaisesRegex(ExportError, "reparse_or_symlink_rejected"):
            execute(self.args(self.write_allowlist([record]), "--dry-run"))


if __name__ == "__main__":
    unittest.main()
