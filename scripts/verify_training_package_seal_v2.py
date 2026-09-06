#!/usr/bin/env python3
"""Verify a complete v2 training-package seal against an external public key."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from crypto_keys import CryptoKeyError, load_ed25519_public_key
from package_sealing import (
    PACKAGE_SEAL_FILENAME,
    PackageSealError,
    load_package_seal,
    validate_package_seal,
)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify all package files, the Merkle root, and the Ed25519 seal signature."
    )
    parser.add_argument("--package-dir", required=True, type=Path)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--registry-entry-id", required=True)
    parser.add_argument("--public-key", required=True, type=Path)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        package_root = args.package_dir.expanduser().resolve()
        public_key_path = args.public_key.expanduser().resolve()
        if _is_relative_to(public_key_path, package_root):
            raise PackageSealError("package_seal_public_key_must_be_outside_package")
        validated = validate_package_seal(
            load_package_seal(package_root / PACKAGE_SEAL_FILENAME),
            package_root=package_root,
            public_key=load_ed25519_public_key(public_key_path),
            expected_dataset_version=args.dataset_version,
            expected_registry_entry_id=args.registry_entry_id,
        )
        print(json.dumps({"status": "ok", **validated.to_dict()}, indent=2))
        return 0
    except (CryptoKeyError, PackageSealError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
