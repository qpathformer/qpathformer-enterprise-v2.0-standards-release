#!/usr/bin/env python3
"""Create an authenticated Q-Pathformer v2 training-authorization artifact."""

from __future__ import annotations

import argparse
import json
from datetime import timedelta
from pathlib import Path
from typing import Optional, Sequence
from uuid import uuid4

from crypto_keys import CryptoKeyError, load_ed25519_private_key
from training_authorization import (
    ALLOWED_TRAINING_SCOPES,
    TrainingAuthorizationError,
    build_training_authorization,
    sha256_file,
    sign_training_authorization,
    utc_now,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a dataset-bound, time-limited v2 training authorization."
    )
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--dataset-path", required=True, type=Path)
    parser.add_argument("--registry-entry-id", required=True)
    parser.add_argument("--decision", required=True, choices=["ALLOW", "DENY"])
    parser.add_argument(
        "--scope",
        action="append",
        choices=sorted(ALLOWED_TRAINING_SCOPES),
        help=(
            "Exactly one explicit scope is required for ALLOW. "
            "Repeated scopes are rejected; DENY accepts no scopes."
        ),
    )
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--decision-source", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument(
        "--private-key",
        required=True,
        type=Path,
        help="Ed25519 authorization-signing private key. It is never written to the artifact.",
    )
    parser.add_argument("--private-key-password-env")
    parser.add_argument("--valid-for-hours", type=int, default=168)
    parser.add_argument("--authorization-id")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--acknowledge-human-decision",
        action="store_true",
        help="Required for ALLOW to confirm this command records an explicit human decision.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        dataset_path = args.dataset_path.expanduser().resolve()
        output_path = args.output.expanduser().resolve()
        if not dataset_path.is_file():
            raise TrainingAuthorizationError(f"dataset_file_not_found:{dataset_path}")
        if output_path.exists():
            raise TrainingAuthorizationError(f"authorization_output_already_exists:{output_path}")
        if args.valid_for_hours <= 0 or args.valid_for_hours > 744:
            raise TrainingAuthorizationError("valid_for_hours_must_be_between_1_and_744")
        if len(args.rationale.strip()) < 20:
            raise TrainingAuthorizationError("rationale_must_contain_at_least_20_characters")

        scopes = list(args.scope or [])
        if args.decision == "ALLOW":
            if not args.acknowledge_human_decision:
                raise TrainingAuthorizationError("allow_requires_acknowledge_human_decision")
            if len(scopes) != 1:
                raise TrainingAuthorizationError("allow_requires_exactly_one_scope")
        elif scopes:
            raise TrainingAuthorizationError("deny_authorization_must_not_include_scopes")

        issued_at = utc_now()
        payload = build_training_authorization(
            authorization_id=args.authorization_id or f"QPAUTH-{uuid4()}",
            decision=args.decision,
            authorized_scopes=scopes,
            dataset_version=args.dataset_version.strip(),
            dataset_sha256=sha256_file(dataset_path),
            registry_entry_id=args.registry_entry_id.strip(),
            reviewer_id=args.reviewer_id.strip(),
            rationale=args.rationale.strip(),
            decision_source=args.decision_source.strip(),
            key_id=args.key_id.strip(),
            issued_at=issued_at,
            expires_at=issued_at + timedelta(hours=args.valid_for_hours),
        )
        signed_payload = sign_training_authorization(
            payload,
            load_ed25519_private_key(
                args.private_key,
                password_env=args.private_key_password_env,
            ),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(signed_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "authorization_id": signed_payload["authorization_id"],
                    "decision": signed_payload["decision"],
                    "authorized_scopes": signed_payload["authorized_scopes"],
                    "dataset_version": signed_payload["dataset_binding"]["dataset_version"],
                    "dataset_sha256": signed_payload["dataset_binding"]["dataset_sha256"],
                    "output": str(output_path),
                    "signature_algorithm": signed_payload["authentication"]["algorithm"],
                    "key_id": signed_payload["authentication"]["key_id"],
                    "public_key_sha256": signed_payload["authentication"]["public_key_sha256"],
                    "key_material_written": False,
                },
                indent=2,
            )
        )
        return 0
    except (CryptoKeyError, TrainingAuthorizationError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
