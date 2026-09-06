#!/usr/bin/env python3
"""Create an Ed25519-authorized and completely sealed copy of a legacy package."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Sequence
from uuid import uuid4

from crypto_keys import (
    CryptoKeyError,
    load_ed25519_private_key,
    load_ed25519_public_key,
    private_key_public_sha256,
)
from package_sealing import (
    MERKLE_ALGORITHM,
    PACKAGE_SEAL_FILENAME,
    PackageSealError,
    write_package_seal,
)
from training_authorization import (
    AUTHORIZATION_FILENAME,
    DEFAULT_TRAINING_SCOPE,
    TrainingAuthorizationError,
    classify_legacy_fine_tuning_flags,
    load_authorization_json,
    require_local_lora_scope,
    sha256_file,
    utc_iso,
    utc_now,
    validate_training_authorization,
)


MANIFEST_FILENAME = "state1_training_manifest.json"
TRAIN_FILENAME = "train.sft.jsonl"
BACKEND_PROFILE_FILENAME = "training_backend_profile.json"


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TrainingAuthorizationError(f"json_not_found:{path}") from exc
    except json.JSONDecodeError as exc:
        raise TrainingAuthorizationError(f"json_invalid:{path}:{exc}") from exc
    if not isinstance(payload, dict):
        raise TrainingAuthorizationError(f"json_root_must_be_object:{path}")
    return payload


def _required_str(payload: Dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TrainingAuthorizationError(f"manifest.{key}_must_be_non_empty_string")
    return value.strip()


def _manifest_record_count(manifest: Dict[str, Any]) -> int:
    for value in (
        manifest.get("record_count"),
        (manifest.get("record_counts") or {}).get("exported_record_count")
        if isinstance(manifest.get("record_counts"), dict)
        else None,
    ):
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
    raise TrainingAuthorizationError("manifest_record_count_missing")


def _legacy_migration(manifest: Dict[str, Any], record_count: int) -> Dict[str, Any]:
    counts = manifest.get("record_counts")
    if isinstance(counts, dict):
        positive = counts.get("fine_tuning_allowed_count")
        negative = counts.get("fine_tuning_disallowed_count")
        if (
            isinstance(positive, int)
            and isinstance(negative, int)
            and positive >= 0
            and negative >= 0
        ):
            missing = max(record_count - positive - negative, 0)
            return classify_legacy_fine_tuning_flags(
                [True] * positive + [False] * negative + [None] * missing
            )
    return classify_legacy_fine_tuning_flags([None] * record_count)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Copy a legacy training package into an Ed25519-authorized and "
            "completely sealed v2 package without mutating the source."
        )
    )
    parser.add_argument("--training-package", required=True, type=Path)
    parser.add_argument("--source-dataset", required=True, type=Path)
    parser.add_argument("--authorization-file", required=True, type=Path)
    parser.add_argument("--authorization-public-key", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--authorization-scope", default=DEFAULT_TRAINING_SCOPE)
    parser.add_argument("--package-seal-private-key", required=True, type=Path)
    parser.add_argument("--package-seal-key-id", required=True)
    parser.add_argument("--package-seal-private-key-password-env")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    staging_package: Optional[Path] = None
    try:
        endpoint_scope = require_local_lora_scope(args.authorization_scope)
        source_package = args.training_package.expanduser().resolve()
        source_dataset = args.source_dataset.expanduser().resolve()
        authorization_source = args.authorization_file.expanduser().resolve()
        authorization_public_key_path = args.authorization_public_key.expanduser().resolve()
        seal_private_key_path = args.package_seal_private_key.expanduser().resolve()
        seal_key_id = args.package_seal_key_id.strip()
        if not seal_key_id:
            raise TrainingAuthorizationError("package_seal_key_id_required")
        if not source_package.is_dir():
            raise TrainingAuthorizationError(f"training_package_not_found:{source_package}")
        if not source_dataset.is_file():
            raise TrainingAuthorizationError(f"source_dataset_not_found:{source_dataset}")
        for filename in (MANIFEST_FILENAME, TRAIN_FILENAME, BACKEND_PROFILE_FILENAME):
            if not (source_package / filename).is_file():
                raise TrainingAuthorizationError(
                    f"training_package_missing_required_file:{filename}"
                )

        source_manifest_path = source_package / MANIFEST_FILENAME
        source_manifest = _load_json(source_manifest_path)
        dataset_version = _required_str(source_manifest, "dataset_version")
        registry_entry_id = _required_str(source_manifest, "registry_entry_id")
        record_count = _manifest_record_count(source_manifest)
        source_dataset_sha256 = sha256_file(source_dataset)
        authorization_payload = load_authorization_json(authorization_source)
        authorization_validation = validate_training_authorization(
            authorization_payload,
            public_key=load_ed25519_public_key(authorization_public_key_path),
            expected_dataset_version=dataset_version,
            expected_dataset_sha256=source_dataset_sha256,
            expected_registry_entry_id=registry_entry_id,
            required_scope=endpoint_scope,
        )
        authorization_sha256 = sha256_file(authorization_source)
        seal_private_key = load_ed25519_private_key(
            seal_private_key_path,
            password_env=args.package_seal_private_key_password_env,
        )
        seal_public_key_sha256 = private_key_public_sha256(seal_private_key)
        if seal_public_key_sha256 == authorization_validation.public_key_sha256:
            raise TrainingAuthorizationError(
                "authorization_and_package_seal_keys_must_be_distinct"
            )

        output_root = args.output_root.expanduser().resolve()
        output_package = output_root / dataset_version
        if output_package.exists():
            raise TrainingAuthorizationError(
                f"migration_output_already_exists:{output_package}"
            )
        if _is_relative_to(authorization_public_key_path, output_package):
            raise TrainingAuthorizationError(
                "authorization_public_key_must_be_outside_training_package"
            )
        if _is_relative_to(seal_private_key_path, output_package):
            raise TrainingAuthorizationError(
                "package_seal_private_key_must_be_outside_training_package"
            )
        output_root.mkdir(parents=True, exist_ok=True)
        staging_package = output_root / f".{dataset_version}.building-{uuid4().hex}"
        shutil.copytree(source_package, staging_package)
        inherited_seal = staging_package / PACKAGE_SEAL_FILENAME
        if inherited_seal.exists():
            inherited_seal.unlink()

        migrated_manifest = dict(source_manifest)
        migrated_manifest["training_manifest_version"] = "v12.2-migrated-auth-seal-v2"
        existing_posture = migrated_manifest.get("authorization_posture")
        if not isinstance(existing_posture, dict):
            existing_posture = {}
        migrated_manifest["authorization_posture"] = {
            **existing_posture,
            "training_preparation_only": True,
            "training_not_executed": True,
            "authorization_not_modified": True,
            "v2_authorization_required": True,
            "v2_authorization_verified": True,
            "authorization_id": authorization_validation.authorization_id,
            "authorized_scope": authorization_validation.required_scope,
            "authorized_scopes": authorization_validation.authorized_scopes,
            "authorization_expires_at_utc": authorization_validation.expires_at_utc,
            "authorization_key_id": authorization_validation.key_id,
            "authorization_public_key_sha256": authorization_validation.public_key_sha256,
            "authorization_artifact_file": AUTHORIZATION_FILENAME,
            "authorization_artifact_sha256": authorization_sha256,
            "source_dataset_sha256": source_dataset_sha256,
            "legacy_migration": _legacy_migration(source_manifest, record_count),
        }
        migrated_manifest["package_seal_posture"] = {
            "complete_package_seal_required": True,
            "signature_algorithm": "Ed25519",
            "inventory_algorithm": "SHA-256",
            "merkle_algorithm": MERKLE_ALGORITHM,
            "package_seal_file": PACKAGE_SEAL_FILENAME,
            "package_seal_key_id": seal_key_id,
            "package_seal_public_key_sha256": seal_public_key_sha256,
            "signing_key_distinct_from_authorization_key": True,
        }
        migrated_manifest["authorization_migration"] = {
            "migration_version": "qpath_training_authorization_migration_v2.2",
            "migrated_at_utc": utc_iso(utc_now()),
            "source_package": str(source_package),
            "source_manifest_sha256": sha256_file(source_manifest_path),
            "source_dataset": str(source_dataset),
            "source_dataset_sha256": source_dataset_sha256,
            "source_package_modified": False,
        }
        output_manifest_path = staging_package / MANIFEST_FILENAME
        output_manifest_path.write_text(
            json.dumps(migrated_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        shutil.copyfile(authorization_source, staging_package / AUTHORIZATION_FILENAME)
        seal = write_package_seal(
            package_root=staging_package,
            dataset_version=dataset_version,
            registry_entry_id=registry_entry_id,
            key_id=seal_key_id,
            private_key=seal_private_key,
        )
        staging_package.rename(output_package)
        staging_package = None

        print(
            json.dumps(
                {
                    "status": "ok",
                    "dataset_version": dataset_version,
                    "authorization_id": authorization_validation.authorization_id,
                    "authorized_scope": authorization_validation.required_scope,
                    "source_package": str(source_package),
                    "output_package": str(output_package),
                    "source_package_modified": False,
                    "package_seal": {
                        "seal_id": seal["seal_id"],
                        "file_count": seal["inventory"]["file_count"],
                        "merkle_root_sha256": seal["merkle"]["root_sha256"],
                        "public_key_sha256": seal["signature"]["public_key_sha256"],
                    },
                },
                indent=2,
            )
        )
        return 0
    except (CryptoKeyError, PackageSealError, TrainingAuthorizationError) as exc:
        if staging_package is not None and staging_package.exists():
            shutil.rmtree(staging_package)
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
