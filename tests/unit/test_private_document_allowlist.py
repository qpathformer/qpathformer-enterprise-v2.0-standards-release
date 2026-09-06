from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from verify_private_workspace import (  # noqa: E402
    STANDARDS_PDF_PATHS, STANDARDS_PDF_SCOPE, document_text, inspect, load_documents,
)


class PrivateDocumentAllowlistTests(unittest.TestCase):
    def make_draft(self, root: Path, extra: dict[str, bytes] | None = None) -> tuple[Path, dict]:
        path = root / "draft.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", '<document><text>Synthetic draft</text></document>')
            for name, data in (extra or {}).items():
                archive.writestr(name, data)
        return path, {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def write_allowlist(self, root: Path, relative: str, duplicate: bool = False) -> None:
        record = {"path": relative, "bytes": 1, "sha256": "0" * 64}
        path = root / "release/provenance/DOCUMENT_ALLOWLIST.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            "scope": "private_tr010_working_draft_only",
            "documents": [record, record] if duplicate else [record],
        }), encoding="utf-8")

    def test_exact_identity_is_read_without_modifying_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path, record = self.make_draft(Path(temporary))
            before = path.read_bytes()
            self.assertIn("Synthetic draft", document_text(path, record))
            self.assertEqual(before, path.read_bytes())

    def test_changed_document_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path, record = self.make_draft(Path(temporary))
            record["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "document_identity_mismatch"):
                document_text(path, record)

    def test_macros_and_embedded_objects_are_rejected(self) -> None:
        for name in ("word/vbaProject.bin", "word/embeddings/object.bin"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                path, record = self.make_draft(Path(temporary), {name: b"synthetic"})
                with self.assertRaisesRegex(ValueError, "document_active_or_embedded_content"):
                    document_text(path, record)

    def test_only_tr010_docx_paths_are_allowed(self) -> None:
        for relative in ("docs/other.docx", "docs/research/tr010/key.pem", "docs/research/tr010/paper.pdf"):
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.write_allowlist(root, relative)
                with self.assertRaisesRegex(ValueError, "document_exception_outside_tr010_docx_scope"):
                    load_documents(root)

    def test_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_allowlist(root, "docs/research/tr010/../../outside.docx")
            with self.assertRaisesRegex(ValueError, "unsafe_relative_path"):
                load_documents(root)

    def test_duplicate_document_exception_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_allowlist(root, "docs/research/tr010/draft.docx", duplicate=True)
            with self.assertRaisesRegex(ValueError, "duplicate_document_exception"):
                load_documents(root)

    def test_valid_exception_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_allowlist(root, "docs/research/tr010/draft.docx")
            self.assertEqual(len(load_documents(root)), 1)


class StandardsPdfAllowlistTests(unittest.TestCase):
    def prepare_workspace(self, root: Path, populate: bool = False) -> list[dict]:
        provenance = root / "release/provenance"
        provenance.mkdir(parents=True)
        (provenance / "SOURCE_SELECTION.json").write_text('{"files": []}', encoding="utf-8")
        (provenance / "STANDARDS_SUBSET.json").write_text('{"retained_files": []}', encoding="utf-8")
        records = []
        if populate:
            for relative in sorted(STANDARDS_PDF_PATHS):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"%PDF-1.7\n% Synthetic envelope for identity tests, not a manuscript.\n%%EOF\n")
                records.append({"path": relative, "bytes": path.stat().st_size,
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        self.write_allowlist(root, records)
        return records

    def write_allowlist(self, root: Path, records: list[dict]) -> None:
        (root / "release/provenance/DOCUMENT_ALLOWLIST.json").write_text(
            json.dumps({"scope": STANDARDS_PDF_SCOPE, "documents": records}), encoding="utf-8")

    def test_pending_conversion_is_not_final_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_workspace(root)
            preparation = inspect(root, False)
            self.assertEqual(preparation["status"], "PASS")
            self.assertFalse(preparation["final_pdf_pair_registered"])
            final = inspect(root, False, require_final_papers=True)
            self.assertEqual(final["status"], "FAIL")
            self.assertIn("final_pdf_pair_not_registered", final["errors"])

    def test_registered_pair_is_verified_without_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = self.prepare_workspace(root, populate=True)
            before = [(root / item["path"]).read_bytes() for item in records]
            result = inspect(root, False, require_final_papers=True)
            self.assertEqual(result["status"], "PASS", result["errors"])
            self.assertEqual(result["allowlisted_documents_verified"], 2)
            self.assertEqual(before, [(root / item["path"]).read_bytes() for item in records])

    def test_unregistered_pdf_is_not_silently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_workspace(root, populate=True)
            self.write_allowlist(root, [])
            result = inspect(root, False)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any(item.startswith("prohibited_file:") for item in result["errors"]))

    def test_word_and_unselected_pdf_paths_are_rejected(self) -> None:
        for relative in ("docs/research/paper.pdf", "docs/research/paper.docx",
                         "docs/research/tr010/draft.docx", "docs/other.pdf"):
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.prepare_workspace(root)
                self.write_allowlist(root, [{"path": relative, "bytes": 1, "sha256": "0" * 64}])
                with self.assertRaisesRegex(ValueError, "document_exception_outside_standards_pdf_pair"):
                    load_documents(root)

    def test_partial_pair_registration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = self.prepare_workspace(root, populate=True)
            self.write_allowlist(root, records[:1])
            with self.assertRaisesRegex(ValueError, "standards_pdf_pair_incomplete"):
                load_documents(root)

    def test_missing_registered_pdf_fails_final_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = self.prepare_workspace(root, populate=True)
            (root / records[0]["path"]).unlink()
            result = inspect(root, False, require_final_papers=True)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any(item.startswith("missing_allowlisted_document:") for item in result["errors"]))

    def test_changed_pdf_identity_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = self.prepare_workspace(root, populate=True)
            path = root / records[0]["path"]
            path.write_bytes(path.read_bytes().replace(b"1.7", b"1.6"))
            with self.assertRaisesRegex(ValueError, "document_identity_mismatch"):
                document_text(path, records[0])

    def test_invalid_pdf_envelope_is_rejected(self) -> None:
        for content in (b"not a PDF\n%%EOF", b"%PDF-1.7\ntruncated"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "paper.pdf"
                path.write_bytes(content)
                record = {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
                with self.assertRaisesRegex(ValueError, "pdf_envelope_invalid"):
                    document_text(path, record)


if __name__ == "__main__":
    unittest.main()
