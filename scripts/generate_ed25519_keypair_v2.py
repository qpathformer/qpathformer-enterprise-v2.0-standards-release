#!/usr/bin/env python3
"""Generate a Q-Pathformer v2 Ed25519 signing keypair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from crypto_keys import CryptoKeyError, write_ed25519_keypair


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an Ed25519 keypair for authorization or package sealing."
    )
    parser.add_argument("--private-key", required=True, type=Path)
    parser.add_argument("--public-key", required=True, type=Path)
    parser.add_argument("--key-id", required=True)
    parser.add_argument(
        "--role",
        required=True,
        choices=["authorization_signer", "package_sealer"],
    )
    parser.add_argument(
        "--password-env",
        help="Optional environment variable containing a private-key password of at least 16 bytes.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        key_id = args.key_id.strip()
        if not key_id:
            raise CryptoKeyError("key_id_required")
        fingerprint = write_ed25519_keypair(
            private_key_path=args.private_key,
            public_key_path=args.public_key,
            password_env=args.password_env,
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "algorithm": "Ed25519",
                    "key_id": key_id,
                    "key_role": args.role,
                    "public_key_sha256": fingerprint,
                    "private_key": str(args.private_key.expanduser().resolve()),
                    "public_key": str(args.public_key.expanduser().resolve()),
                    "private_key_encrypted": bool(args.password_env),
                },
                indent=2,
            )
        )
        return 0
    except CryptoKeyError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
