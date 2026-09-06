#!/usr/bin/env python3
"""Deterministic inventory, Merkle sealing, and Ed25519 package verification."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from crypto_keys import (
    SIGNATURE_ALGORITHM,
    CryptoKeyError,
    private_key_public_sha256,
    public_key_sha256,
    sign_bytes,
    verify_bytes,
)


PACKAGE_SEAL_FILENAME = "package_seal.json"
TRAINING_MANIFEST_FILENAME = "state1_training_manifest.json"
PACKAGE_SEAL_SCHEMA_VERSION = "qpath_package_seal_v2.0"
CANONICALIZATION_METHOD = "qpath-json-sort-keys-v1"
INVENTORY_ALGORITHM = "SHA-256"
MERKLE_ALGORITHM = "qpath-merkle-sha256-v1"
LEAF_DOMAIN = b"qpath-file-v1\x00"
NODE_DOMAIN = b"qpath-node-v1\x00"


class PackageSealError(RuntimeError):
    """Raised when a package cannot be sealed or does not match its seal."""


@dataclass(frozen=True)
class ValidatedPackageSeal:
    seal_id: str
    dataset_version: str
    registry_entry_id: str
    file_count: int
    merkle_root_sha256: str
    key_id: str
    public_key_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seal_schema_version": PACKAGE_SEAL_SCHEMA_VERSION,
            "seal_id": self.seal_id,
            "dataset_version": self.dataset_version,
            "registry_entry_id": self.registry_entry_id,
            "file_count": self.file_count,
            "merkle_root_sha256": self.merkle_root_sha256,
            "signature": {
                "algorithm": SIGNATURE_ALGORITHM,
                "key_id": self.key_id,
                "public_key_sha256": self.public_key_sha256,
                "verified": True,
            },
        }


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_package_root(package_root: Path) -> Path:
    root = package_root.expanduser().resolve()
    if not root.is_dir():
        raise PackageSealError(f"package_root_not_found:{root}")
    if root.is_symlink():
        raise PackageSealError(f"package_root_must_not_be_symlink:{root}")
    return root


def build_package_inventory(package_root: Path) -> List[Dict[str, Any]]:
    root = _require_package_root(package_root)
    entries: List[Dict[str, Any]] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise PackageSealError(f"package_symlink_not_allowed:{path}")
        if not path.is_file():
            continue
        relative_path = path.relative_to(root).as_posix()
        if relative_path == PACKAGE_SEAL_FILENAME:
            continue
        entries.append(
            {
                "path": relative_path,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    entries.sort(key=lambda item: item["path"].encode("utf-8"))
    if not entries:
        raise PackageSealError("package_contains_no_sealable_files")
    return entries


def validate_training_manifest_binding(
    package_root: Path,
    *,
    expected_dataset_version: str,
    expected_registry_entry_id: str,
) -> None:
    root = _require_package_root(package_root)
    manifest_path = root / TRAINING_MANIFEST_FILENAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageSealError(f"training_manifest_not_found:{manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise PackageSealError(f"training_manifest_json_invalid:{manifest_path}:{exc}") from exc
    if not isinstance(manifest, dict):
        raise PackageSealError("training_manifest_root_must_be_object")
    dataset_version = _require_str(
        manifest.get("dataset_version"),
        "training_manifest.dataset_version",
    )
    registry_entry_id = _require_str(
        manifest.get("registry_entry_id"),
        "training_manifest.registry_entry_id",
    )
    if dataset_version != expected_dataset_version:
        raise PackageSealError(
            "training_manifest_dataset_version_mismatch:"
            f"{dataset_version}!={expected_dataset_version}"
        )
    if registry_entry_id != expected_registry_entry_id:
        raise PackageSealError(
            "training_manifest_registry_entry_mismatch:"
            f"{registry_entry_id}!={expected_registry_entry_id}"
        )


def _leaf_hash(entry: Dict[str, Any]) -> bytes:
    payload = (
        LEAF_DOMAIN
        + entry["path"].encode("utf-8")
        + b"\x00"
        + str(entry["size_bytes"]).encode("ascii")
        + b"\x00"
        + bytes.fromhex(entry["sha256"])
    )
    return hashlib.sha256(payload).digest()


def calculate_merkle_root(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        raise PackageSealError("merkle_inventory_must_not_be_empty")
    level = [_leaf_hash(entry) for entry in entries]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            hashlib.sha256(NODE_DOMAIN + level[index] + level[index + 1]).digest()
            for index in range(0, len(level), 2)
        ]
    return level[0].hex()


def canonical_package_seal_bytes(payload: Dict[str, Any]) -> bytes:
    canonical_payload = copy.deepcopy(payload)
    signature = canonical_payload.get("signature")
    if not isinstance(signature, dict):
        raise PackageSealError("package_seal.signature_must_be_object")
    signature.pop("value", None)
    return json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def build_package_seal(
    *,
    package_root: Path,
    dataset_version: str,
    registry_entry_id: str,
    key_id: str,
    private_key: Ed25519PrivateKey,
    seal_id: Optional[str] = None,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_dataset_version = _require_str(dataset_version, "dataset_version")
    normalized_registry_entry_id = _require_str(registry_entry_id, "registry_entry_id")
    normalized_key_id = _require_str(key_id, "key_id")
    validate_training_manifest_binding(
        package_root,
        expected_dataset_version=normalized_dataset_version,
        expected_registry_entry_id=normalized_registry_entry_id,
    )
    entries = build_package_inventory(package_root)
    payload: Dict[str, Any] = {
        "seal_schema_version": PACKAGE_SEAL_SCHEMA_VERSION,
        "seal_id": seal_id or f"QPSEAL-{uuid4()}",
        "created_at_utc": created_at_utc or _utc_now_iso(),
        "package_binding": {
            "dataset_version": normalized_dataset_version,
            "registry_entry_id": normalized_registry_entry_id,
        },
        "inventory": {
            "algorithm": INVENTORY_ALGORITHM,
            "file_count": len(entries),
            "entries": entries,
        },
        "merkle": {
            "algorithm": MERKLE_ALGORITHM,
            "root_sha256": calculate_merkle_root(entries),
        },
        "signature": {
            "algorithm": SIGNATURE_ALGORITHM,
            "canonicalization": CANONICALIZATION_METHOD,
            "key_id": normalized_key_id,
            "public_key_sha256": private_key_public_sha256(private_key),
            "value": "",
        },
    }
    payload["signature"]["value"] = sign_bytes(
        private_key,
        canonical_package_seal_bytes(payload),
    )
    return payload


def write_package_seal(
    *,
    package_root: Path,
    dataset_version: str,
    registry_entry_id: str,
    key_id: str,
    private_key: Ed25519PrivateKey,
) -> Dict[str, Any]:
    root = _require_package_root(package_root)
    seal_path = root / PACKAGE_SEAL_FILENAME
    if seal_path.exists():
        raise PackageSealError(f"package_seal_already_exists:{seal_path}")
    payload = build_package_seal(
        package_root=root,
        dataset_version=dataset_version,
        registry_entry_id=registry_entry_id,
        key_id=key_id,
        private_key=private_key,
    )
    seal_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def load_package_seal(path: Path) -> Dict[str, Any]:
    normalized_path = path.expanduser().resolve()
    try:
        payload = json.loads(normalized_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageSealError(f"package_seal_not_found:{normalized_path}") from exc
    except json.JSONDecodeError as exc:
        raise PackageSealError(f"package_seal_json_invalid:{normalized_path}:{exc}") from exc
    if not isinstance(payload, dict):
        raise PackageSealError("package_seal_root_must_be_object")
    return payload


def validate_package_seal(
    payload: Dict[str, Any],
    *,
    package_root: Path,
    public_key: Ed25519PublicKey,
    expected_dataset_version: str,
    expected_registry_entry_id: str,
) -> ValidatedPackageSeal:
    _require_exact_keys(
        payload,
        {
            "seal_schema_version",
            "seal_id",
            "created_at_utc",
            "package_binding",
            "inventory",
            "merkle",
            "signature",
        },
        "package_seal",
    )
    version = _require_str(payload.get("seal_schema_version"), "seal_schema_version")
    if version != PACKAGE_SEAL_SCHEMA_VERSION:
        raise PackageSealError(f"package_seal_schema_version_unsupported:{version}")
    seal_id = _require_str(payload.get("seal_id"), "seal_id")
    _require_str(payload.get("created_at_utc"), "created_at_utc")

    binding = _require_dict(payload.get("package_binding"), "package_binding")
    _require_exact_keys(binding, {"dataset_version", "registry_entry_id"}, "package_binding")
    dataset_version = _require_str(binding.get("dataset_version"), "package_binding.dataset_version")
    registry_entry_id = _require_str(
        binding.get("registry_entry_id"),
        "package_binding.registry_entry_id",
    )
    if dataset_version != expected_dataset_version:
        raise PackageSealError(
            f"package_seal_dataset_version_mismatch:{dataset_version}!={expected_dataset_version}"
        )
    if registry_entry_id != expected_registry_entry_id:
        raise PackageSealError(
            "package_seal_registry_entry_mismatch:"
            f"{registry_entry_id}!={expected_registry_entry_id}"
        )
    validate_training_manifest_binding(
        package_root,
        expected_dataset_version=expected_dataset_version,
        expected_registry_entry_id=expected_registry_entry_id,
    )

    signature = _require_dict(payload.get("signature"), "signature")
    _require_exact_keys(
        signature,
        {
            "algorithm",
            "canonicalization",
            "key_id",
            "public_key_sha256",
            "value",
        },
        "signature",
    )
    algorithm = _require_str(signature.get("algorithm"), "signature.algorithm")
    if algorithm != SIGNATURE_ALGORITHM:
        raise PackageSealError(f"package_seal_signature_algorithm_unsupported:{algorithm}")
    canonicalization = _require_str(
        signature.get("canonicalization"),
        "signature.canonicalization",
    )
    if canonicalization != CANONICALIZATION_METHOD:
        raise PackageSealError(
            f"package_seal_canonicalization_unsupported:{canonicalization}"
        )
    key_id = _require_str(signature.get("key_id"), "signature.key_id")
    recorded_fingerprint = _require_sha256(
        signature.get("public_key_sha256"),
        "signature.public_key_sha256",
    )
    trusted_fingerprint = public_key_sha256(public_key)
    if recorded_fingerprint != trusted_fingerprint:
        raise PackageSealError(
            "package_seal_public_key_mismatch:"
            f"{recorded_fingerprint}!={trusted_fingerprint}"
        )
    signature_value = _require_str(signature.get("value"), "signature.value")
    try:
        verify_bytes(public_key, canonical_package_seal_bytes(payload), signature_value)
    except CryptoKeyError as exc:
        raise PackageSealError(f"package_seal_{exc}") from exc

    inventory = _require_dict(payload.get("inventory"), "inventory")
    _require_exact_keys(inventory, {"algorithm", "file_count", "entries"}, "inventory")
    if _require_str(inventory.get("algorithm"), "inventory.algorithm") != INVENTORY_ALGORITHM:
        raise PackageSealError("package_inventory_algorithm_unsupported")
    recorded_count = _require_int(inventory.get("file_count"), "inventory.file_count")
    recorded_entries = inventory.get("entries")
    if not isinstance(recorded_entries, list):
        raise PackageSealError("inventory.entries_must_be_array")
    normalized_recorded_entries = [
        _validate_inventory_entry(entry, index)
        for index, entry in enumerate(recorded_entries)
    ]
    if recorded_count != len(normalized_recorded_entries):
        raise PackageSealError(
            f"package_inventory_count_mismatch:{recorded_count}!={len(normalized_recorded_entries)}"
        )
    if [entry["path"] for entry in normalized_recorded_entries] != sorted(
        (entry["path"] for entry in normalized_recorded_entries),
        key=lambda value: value.encode("utf-8"),
    ):
        raise PackageSealError("package_inventory_paths_not_sorted")

    actual_entries = build_package_inventory(package_root)
    if normalized_recorded_entries != actual_entries:
        raise PackageSealError("package_inventory_verification_failed")

    merkle = _require_dict(payload.get("merkle"), "merkle")
    _require_exact_keys(merkle, {"algorithm", "root_sha256"}, "merkle")
    if _require_str(merkle.get("algorithm"), "merkle.algorithm") != MERKLE_ALGORITHM:
        raise PackageSealError("package_merkle_algorithm_unsupported")
    recorded_root = _require_sha256(merkle.get("root_sha256"), "merkle.root_sha256")
    actual_root = calculate_merkle_root(actual_entries)
    if recorded_root != actual_root:
        raise PackageSealError(
            f"package_merkle_root_mismatch:{recorded_root}!={actual_root}"
        )

    return ValidatedPackageSeal(
        seal_id=seal_id,
        dataset_version=dataset_version,
        registry_entry_id=registry_entry_id,
        file_count=recorded_count,
        merkle_root_sha256=actual_root,
        key_id=key_id,
        public_key_sha256=trusted_fingerprint,
    )


def _validate_inventory_entry(value: Any, index: int) -> Dict[str, Any]:
    label = f"inventory.entries[{index}]"
    entry = _require_dict(value, label)
    _require_exact_keys(entry, {"path", "size_bytes", "sha256"}, label)
    path = _require_str(entry.get("path"), f"{label}.path")
    normalized_path = Path(path.replace("\\", "/"))
    if normalized_path.is_absolute() or ".." in normalized_path.parts:
        raise PackageSealError(f"{label}.path_must_be_package_relative")
    size_bytes = _require_int(entry.get("size_bytes"), f"{label}.size_bytes")
    if size_bytes < 0:
        raise PackageSealError(f"{label}.size_bytes_must_be_non_negative")
    return {
        "path": path,
        "size_bytes": size_bytes,
        "sha256": _require_sha256(entry.get("sha256"), f"{label}.sha256"),
    }


def _require_dict(value: Any, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise PackageSealError(f"{label}_must_be_object")
    return value


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PackageSealError(f"{label}_must_be_non_empty_string")
    return value.strip()


def _require_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise PackageSealError(f"{label}_must_be_integer")
    return value


def _require_sha256(value: Any, label: str) -> str:
    normalized = _require_str(value, label).lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise PackageSealError(f"{label}_must_be_sha256_hex")
    return normalized


def _require_exact_keys(value: Dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        raise PackageSealError(f"{label}_missing_keys:{','.join(missing)}")
    if unexpected:
        raise PackageSealError(f"{label}_unexpected_keys:{','.join(unexpected)}")
