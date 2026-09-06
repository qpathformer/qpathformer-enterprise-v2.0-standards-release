#!/usr/bin/env python3
"""Create a complete Ed25519 package seal for a prepared training package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from crypto_keys import CryptoKeyError, load_ed25519_private_key
from package_sealing import PackageSealError, write_package_seal


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory, Merkle-seal, and sign a complete v2 training package."
    )
    parser.add_argument("--package-dir", required=True, type=Path)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--registry-entry-id", required=True)
    parser.add_argument("--private-key", required=True, type=Path)
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--private-key-password-env")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        package_root = args.package_dir.expanduser().resolve()
        private_key_path = args.private_key.expanduser().resolve()
        if _is_relative_to(private_key_path, package_root):
            raise PackageSealError("package_seal_private_key_must_be_outside_package")
        payload = write_package_seal(
            package_root=package_root,
            dataset_version=args.dataset_version,
            registry_entry_id=args.registry_entry_id,
            key_id=args.key_id,
            private_key=load_ed25519_private_key(
                private_key_path,
                password_env=args.private_key_password_env,
            ),
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "seal_id": payload["seal_id"],
                    "package_dir": str(package_root),
                    "file_count": payload["inventory"]["file_count"],
                    "merkle_root_sha256": payload["merkle"]["root_sha256"],
                    "public_key_sha256": payload["signature"]["public_key_sha256"],
                    "private_key_written_to_package": False,
                },
                indent=2,
            )
        )
        return 0
    except (CryptoKeyError, PackageSealError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
