#!/usr/bin/env python3
"""Read-only checks for the local private-development selection, not a release gate."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

from jsonschema.validators import validator_for


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = "release/provenance"
FORBIDDEN_SUFFIXES = {
    ".pdf", ".docx", ".zip", ".pem", ".key", ".p12", ".pfx",
    ".safetensors", ".gguf", ".pt", ".pth", ".bin", ".pyc",
}
DOCUMENT_ALLOWLIST = f"{PROVENANCE}/DOCUMENT_ALLOWLIST.json"
MAX_DOCUMENT_XML_BYTES = 32 * 1024 * 1024
STANDARDS_PDF_SCOPE = "standards_tr010_pdf_pair_only"
STANDARDS_PDF_PATHS = frozenset({
    "docs/research/APOD-TR-010_STANDARDS_REVIEW.pdf",
    "docs/research/APOD-TR-010-R_STANDARDS_REVIEW.pdf",
})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_link(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def safe_path(root: Path, value: str) -> Path:
    relative = PurePosixPath(value)
    if (
        not value or relative.is_absolute() or "\\" in value or ":" in value
        or ".." in relative.parts or relative.as_posix() != value
    ):
        raise ValueError(f"unsafe_relative_path:{value}")
    result = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and is_link(current):
            raise ValueError(f"reparse_or_symlink:{value}")
    return result


def load_documents(root: Path) -> dict[str, dict]:
    payload = json.loads(safe_path(root, DOCUMENT_ALLOWLIST).read_text(encoding="utf-8-sig"))
    scope = payload.get("scope")
    if scope not in {"private_tr010_working_draft_only", STANDARDS_PDF_SCOPE}:
        raise ValueError("document_allowlist_scope_invalid")
    documents: dict[str, dict] = {}
    seen: set[str] = set()
    for record in payload["documents"]:
        relative = record["path"]
        path = safe_path(root, relative)
        if scope == STANDARDS_PDF_SCOPE and relative not in STANDARDS_PDF_PATHS:
            raise ValueError("document_exception_outside_standards_pdf_pair")
        if scope == "private_tr010_working_draft_only" and (not relative.startswith("docs/research/tr010/") or path.suffix != ".docx"):
            raise ValueError("document_exception_outside_tr010_docx_scope")
        if relative.casefold() in seen:
            raise ValueError("duplicate_document_exception")
        if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            raise ValueError("document_digest_invalid")
        if type(record["bytes"]) is not int or record["bytes"] <= 0:
            raise ValueError("document_size_invalid")
        seen.add(relative.casefold())
        documents[relative] = record
    # An empty PDF allowlist represents pre-conversion preparation, not a finished release.
    if scope == STANDARDS_PDF_SCOPE and documents and set(documents) != STANDARDS_PDF_PATHS:
        raise ValueError("standards_pdf_pair_incomplete")
    return documents


def document_text(path: Path, record: dict) -> str:
    if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
        raise ValueError("document_identity_mismatch")
    if path.suffix == ".pdf":
        content = path.read_bytes()
        if not content.startswith(b"%PDF-") or not content.rstrip().endswith(b"%%EOF"):
            raise ValueError("pdf_envelope_invalid")
        # Identity/envelope check only; compressed content and visual layout need separate review.
        return content.decode("latin-1")
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if "word/document.xml" not in names or len(names) != len(set(names)):
            raise ValueError("document_package_invalid")
        if len(infos) > 500 or sum(info.file_size for info in infos) > MAX_DOCUMENT_XML_BYTES:
            raise ValueError("document_package_size_limit")
        if any(name.lower().endswith(".bin") or "/embeddings/" in name.lower() for name in names):
            raise ValueError("document_active_or_embedded_content")
        fragments = []
        for name in names:
            if name.endswith((".xml", ".rels")):
                # Parse in memory only. Never extract or reserialize the draft.
                tree = ElementTree.fromstring(archive.read(name))
                fragments.append("".join(tree.itertext()))
        return "\n".join(fragments)


def inspect(root: Path, strict: bool, require_final_papers: bool = False) -> dict:
    errors: list[str] = []
    changed: list[str] = []
    files: list[Path] = []
    if is_link(root):
        raise ValueError("repository_root_must_not_be_reparse_or_symlink")
    documents = load_documents(root)
    missing_final_papers = sorted(STANDARDS_PDF_PATHS - documents.keys())
    if require_final_papers and missing_final_papers:
        errors.append("final_pdf_pair_not_registered")
    for relative in documents:
        if not safe_path(root, relative).is_file():
            errors.append(f"missing_allowlisted_document:{relative}")
    for base, directories, names in os.walk(root, followlinks=False):
        for name in list(directories):
            path = Path(base) / name
            relative = path.relative_to(root).as_posix()
            if is_link(path):
                errors.append(f"reparse_or_symlink:{relative}")
                directories.remove(name)
            elif relative in {".git", ".local", ".venv"}:
                directories.remove(name)
            elif name in {".git", "__pycache__", "legacy_reference"} or name.startswith("_upstream"):
                errors.append(f"prohibited_directory:{relative}")
                directories.remove(name)
        for name in names:
            path = Path(base) / name
            relative = path.relative_to(root).as_posix()
            if is_link(path):
                errors.append(f"reparse_or_symlink:{relative}")
                continue
            files.append(path)
            if (path.suffix.lower() in FORBIDDEN_SUFFIXES and relative not in documents) or name.startswith(".env"):
                errors.append(f"prohibited_file:{relative}")
            if relative.startswith("path_") and name != "README.md":
                errors.append(f"unreviewed_path_data:{relative}")
            if relative.startswith("shared/standards/access_pod/generated/"):
                errors.append(f"unreviewed_generated_score:{relative}")
            if relative in {"shared/registry/run_registry.json", "shared/registry/state1_dataset_registry.json"}:
                errors.append(f"live_registry:{relative}")

    def load(relative: str):
        return json.loads(safe_path(root, relative).read_text(encoding="utf-8-sig"))

    selection = load(f"{PROVENANCE}/SOURCE_SELECTION.json")
    seen: set[str] = set()
    for record in selection["files"]:
        relative = record["destination_path"]
        if relative.casefold() in seen:
            errors.append(f"duplicate_destination:{relative}")
            continue
        seen.add(relative.casefold())
        path = safe_path(root, relative)
        if not path.is_file():
            errors.append(f"missing_selected_file:{relative}")
        elif sha256(path) != record["destination_sha256"]:
            changed.append(relative)
            if strict or record["immutable_copy"]:
                errors.append(f"origin_bytes_changed:{relative}")

    parsed_python = parsed_json = schemas = checked_documents = 0
    # Avoid echoing any potentially sensitive matched contents into logs.
    key_pattern = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")
    token_pattern = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            if relative in documents:
                text = document_text(path, documents[relative])
                checked_documents += 1
            else:
                text = path.read_text(encoding="utf-8-sig")
            if key_pattern.search(text) or token_pattern.search(text):
                errors.append(f"possible_secret:{relative}")
            if path.suffix == ".py":
                ast.parse(text, filename=relative)
                parsed_python += 1
            if path.suffix == ".json":
                payload = json.loads(text)
                parsed_json += 1
                if isinstance(payload, dict) and "$schema" in payload:
                    validator_for(payload).check_schema(payload)
                    schemas += 1
        except Exception as exc:
            errors.append(f"parse_or_schema_error:{relative}:{type(exc).__name__}")

    subset = load(f"{PROVENANCE}/STANDARDS_SUBSET.json")
    for record in subset["retained_files"]:
        path = safe_path(root, record["destination_path"])
        if not path.is_file() or sha256(path) != record["physical_sha256"]:
            errors.append(f"standards_physical_mismatch:{record['destination_path']}")
        elif record.get("manifest_sha256"):
            content = path.read_bytes()
            if record["comparison"] == "CANONICAL_LF_MATCH":
                content = content.replace(b"\r\n", b"\n")
            if len(content) != record["manifest_bytes"] or hashlib.sha256(content).hexdigest() != record["manifest_sha256"]:
                errors.append(f"standards_manifest_mismatch:{record['destination_path']}")

    for workflow in (root / ".github" / "workflows").glob("*.yml"):
        for action in re.findall(r"(?m)^\s*uses:\s*(\S+)", workflow.read_text(encoding="utf-8")):
            if not re.fullmatch(r"[^@]+@[0-9a-f]{40}", action):
                errors.append(f"unpinned_action:{workflow.name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "scope": "private_workspace_preparation_not_release_or_authorization_approval",
        "verify_origin_bytes": strict,
        "file_count": len(files),
        "selected_copy_count": len(selection["files"]),
        "python_ast_count": parsed_python,
        "json_parse_count": parsed_json,
        "schema_definition_count": schemas,
        "allowlisted_working_drafts_verified": checked_documents,
        "allowlisted_documents_verified": checked_documents,
        "final_pdf_pair_registered": not missing_final_papers,
        "require_final_papers": require_final_papers,
        "unregistered_final_pdf_paths": missing_final_papers,
        "active_inherited_changes": changed,
        "errors": errors,
        "limits": [
            "No model execution or training.",
            "Secret-pattern scan is limited, not a complete security audit.",
            "No legal, human-release, GitHub-visibility or single-scope approval.",
            "Local machine folders .git, .local and .venv are excluded.",
            "PDF checks establish exact registered bytes and a basic envelope, not visual correctness or complete PDF safety.",
            "A preparation PASS with unregistered final PDFs is not readiness to seal or publish.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-origin-bytes", action="store_true")
    parser.add_argument("--require-final-papers", action="store_true", help="Fail unless both final PDFs are registered, present and hash-matched.")
    args = parser.parse_args()
    try:
        result = inspect(ROOT, args.verify_origin_bytes, args.require_final_papers)
    except Exception as exc:
        result = {"status": "FAIL", "errors": [f"verification_error:{type(exc).__name__}:{exc}"]}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
