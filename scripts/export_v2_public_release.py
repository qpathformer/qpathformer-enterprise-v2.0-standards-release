#!/usr/bin/env python3
"""Fail-closed allowlist exporter for the Q-Pathformer v2 public tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence


TEXT_EXTENSIONS = {
    ".gitignore",
    ".jinja",
    ".json",
    ".jsonl",
    ".md",
    ".ps1",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}
ALLOWED_POLICIES = {"preserve", "normalize_lf", "preserve_by_extension"}


class ExportError(RuntimeError):
    """Raised when an export invariant is not satisfied."""


@dataclass(frozen=True)
class ExportEntry:
    relative_path: str
    source_path: Path
    target_path: Path
    source_bytes: int
    source_sha256: str
    target_bytes: int
    target_sha256: str
    policy: str
    applied_transformation: str
    content: bytes


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_reparse_or_symlink(path: Path) -> bool:
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def assert_safe_existing_chain(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ExportError(f"path_outside_root:{path}") from exc

    current = root
    if current.exists() and is_reparse_or_symlink(current):
        raise ExportError(f"reparse_or_symlink_rejected:{current}")
    for part in relative.parts:
        current = current / part
        if current.exists() and is_reparse_or_symlink(current):
            raise ExportError(f"reparse_or_symlink_rejected:{current}")


def validate_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExportError("allowlist_path_missing")
    if "\\" in value:
        raise ExportError(f"allowlist_path_must_use_forward_slashes:{value}")
    path = PurePosixPath(value)
    if path.is_absolute() or value.startswith("/"):
        raise ExportError(f"absolute_allowlist_path_rejected:{value}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ExportError(f"unsafe_allowlist_path_rejected:{value}")
    if path.parts and path.parts[0].lower() == ".git":
        raise ExportError(f"git_metadata_path_rejected:{value}")
    return path.as_posix()


def read_allowlist(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExportError(f"allowlist_read_failed:{path}:{exc}") from exc
    if not isinstance(payload, dict):
        raise ExportError("allowlist_must_be_object")
    records = payload.get("resolved_files")
    if not isinstance(records, list) or not records:
        raise ExportError("allowlist_resolved_files_missing")
    if not all(isinstance(item, dict) for item in records):
        raise ExportError("allowlist_record_invalid")
    return payload, records


def normalize_lf(content: bytes, relative_path: str) -> bytes:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ExportError(f"active_text_not_utf8:{relative_path}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def transform_content(content: bytes, policy: str, relative_path: str) -> tuple[bytes, str]:
    if policy not in ALLOWED_POLICIES:
        raise ExportError(f"unsupported_byte_policy:{relative_path}:{policy}")
    if policy == "preserve":
        return content, "preserve"
    if policy == "normalize_lf":
        return normalize_lf(content, relative_path), "normalize_lf"
    suffix = Path(relative_path).suffix.lower()
    if suffix in TEXT_EXTENSIONS or Path(relative_path).name == ".gitignore":
        return normalize_lf(content, relative_path), "normalize_lf"
    return content, "preserve"


def ensure_distinct_roots(source_root: Path, target_root: Path) -> None:
    source = source_root.resolve()
    target = target_root.resolve(strict=False)
    if source == target:
        raise ExportError("source_and_target_are_identical")
    if source in target.parents:
        raise ExportError("target_inside_source_rejected")
    if target in source.parents:
        raise ExportError("source_inside_target_rejected")


def target_is_empty(target_root: Path) -> bool:
    if not target_root.exists():
        return True
    if not target_root.is_dir():
        return False
    return next(target_root.iterdir(), None) is None


def build_export_entries(
    source_root: Path,
    target_root: Path,
    records: Iterable[dict[str, Any]],
) -> list[ExportEntry]:
    entries: list[ExportEntry] = []
    seen: set[str] = set()
    for record in records:
        relative_path = validate_relative_path(record.get("path"))
        path_key = relative_path.casefold()
        if path_key in seen:
            raise ExportError(f"duplicate_allowlist_path:{relative_path}")
        seen.add(path_key)

        source_path = source_root.joinpath(*PurePosixPath(relative_path).parts)
        target_path = target_root.joinpath(*PurePosixPath(relative_path).parts)
        assert_safe_existing_chain(source_root, source_path)
        if not source_path.is_file():
            raise ExportError(f"source_file_missing:{relative_path}")

        expected_size = record.get("source_bytes")
        expected_hash = record.get("source_sha256")
        if not isinstance(expected_size, int) or expected_size < 0:
            raise ExportError(f"source_size_missing:{relative_path}")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ExportError(f"source_sha256_missing:{relative_path}")

        content = source_path.read_bytes()
        actual_hash = sha256_bytes(content)
        if len(content) != expected_size:
            raise ExportError(
                f"source_size_mismatch:{relative_path}:{len(content)}!={expected_size}"
            )
        if actual_hash != expected_hash.lower():
            raise ExportError(
                f"source_sha256_mismatch:{relative_path}:{actual_hash}!={expected_hash.lower()}"
            )

        policy = record.get("byte_policy")
        if not isinstance(policy, str):
            raise ExportError(f"byte_policy_missing:{relative_path}")
        target_content, transformation = transform_content(content, policy, relative_path)
        entries.append(
            ExportEntry(
                relative_path=relative_path,
                source_path=source_path,
                target_path=target_path,
                source_bytes=len(content),
                source_sha256=actual_hash,
                target_bytes=len(target_content),
                target_sha256=sha256_bytes(target_content),
                policy=policy,
                applied_transformation=transformation,
                content=target_content,
            )
        )
    return sorted(entries, key=lambda item: item.relative_path)


def tree_digest(entries: Iterable[ExportEntry]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry.relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry.target_sha256.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def target_regular_files(target_root: Path) -> set[str]:
    files: set[str] = set()
    for current_root, dir_names, file_names in os.walk(target_root, followlinks=False):
        current = Path(current_root)
        dir_names[:] = [name for name in dir_names if name != ".git"]
        for name in tuple(dir_names) + tuple(file_names):
            candidate = current / name
            if candidate.exists() and is_reparse_or_symlink(candidate):
                raise ExportError(f"target_reparse_or_symlink_rejected:{candidate}")
        for name in file_names:
            candidate = current / name
            relative = candidate.relative_to(target_root).as_posix()
            files.add(relative)
    return files


def verify_target(target_root: Path, entries: Sequence[ExportEntry]) -> None:
    if not target_root.is_dir():
        raise ExportError(f"target_directory_missing:{target_root}")
    expected = {entry.relative_path for entry in entries}
    actual = target_regular_files(target_root)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise ExportError(f"target_files_missing:{','.join(missing)}")
    if extra:
        raise ExportError(f"target_files_unexpected:{','.join(extra)}")
    for entry in entries:
        assert_safe_existing_chain(target_root, entry.target_path)
        if entry.target_path.stat().st_size != entry.target_bytes:
            raise ExportError(f"target_size_mismatch:{entry.relative_path}")
        if sha256_file(entry.target_path) != entry.target_sha256:
            raise ExportError(f"target_sha256_mismatch:{entry.relative_path}")


def write_export(target_root: Path, entries: Sequence[ExportEntry]) -> None:
    if not target_is_empty(target_root):
        raise ExportError(f"target_not_empty:{target_root}")
    target_root.mkdir(parents=True, exist_ok=True)
    assert_safe_existing_chain(target_root, target_root)
    for entry in entries:
        entry.target_path.parent.mkdir(parents=True, exist_ok=True)
        assert_safe_existing_chain(target_root, entry.target_path.parent)
        entry.target_path.write_bytes(entry.content)
    verify_target(target_root, entries)


def build_report(
    mode: str,
    source_root: Path,
    target_root: Path,
    allowlist_path: Path,
    allowlist_payload: dict[str, Any],
    entries: Sequence[ExportEntry],
) -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": mode,
        "generated_at_utc": utc_now(),
        "source_root_logical": allowlist_payload.get("source_root_logical"),
        "target_root_logical": allowlist_payload.get("target_root_logical"),
        "source_root_local": str(source_root),
        "target_root_local": str(target_root),
        "allowlist_path": str(allowlist_path),
        "allowlist_document_id": allowlist_payload.get("document_id"),
        "file_count": len(entries),
        "source_bytes": sum(item.source_bytes for item in entries),
        "target_bytes": sum(item.target_bytes for item in entries),
        "target_tree_sha256": tree_digest(entries),
        "files": [
            {
                "path": item.relative_path,
                "source_bytes": item.source_bytes,
                "source_sha256": item.source_sha256,
                "target_bytes": item.target_bytes,
                "target_sha256": item.target_sha256,
                "byte_policy": item.policy,
                "applied_transformation": item.applied_transformation,
            }
            for item in entries
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--allowlist", required=True, type=Path)
    parser.add_argument("--log-output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    return parser.parse_args(argv)


def execute(args: argparse.Namespace) -> dict[str, Any]:
    source_root = args.source_root.expanduser().resolve()
    target_root = args.target_root.expanduser().resolve(strict=False)
    allowlist_path = args.allowlist.expanduser().resolve()
    if not source_root.is_dir():
        raise ExportError(f"source_root_missing:{source_root}")
    ensure_distinct_roots(source_root, target_root)
    payload, records = read_allowlist(allowlist_path)
    entries = build_export_entries(source_root, target_root, records)

    if args.verify_only:
        verify_target(target_root, entries)
        mode = "verify_only"
    elif args.dry_run:
        if not target_is_empty(target_root):
            raise ExportError(f"target_not_empty:{target_root}")
        mode = "dry_run"
    else:
        write_export(target_root, entries)
        mode = "export"

    report = build_report(
        mode,
        source_root,
        target_root,
        allowlist_path,
        payload,
        entries,
    )
    if args.log_output is not None:
        log_output = args.log_output.expanduser().resolve()
        if target_root == log_output or target_root in log_output.parents:
            raise ExportError("export_log_must_be_outside_target")
        log_output.parent.mkdir(parents=True, exist_ok=True)
        log_output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = execute(args)
    except ExportError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
