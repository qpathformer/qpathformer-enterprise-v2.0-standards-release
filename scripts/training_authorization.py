#!/usr/bin/env python3
"""Shared v2.2 single-scope authorization contract and Ed25519 verification."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

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


AUTHORIZATION_SCHEMA_VERSION = "qpath_training_authorization_v2.2"
AUTHORIZATION_FILENAME = "training_authorization.json"
CANONICALIZATION_METHOD = "qpath-json-sort-keys-v1"
DEFAULT_TRAINING_SCOPE = "validation_parameter_update"
LOCAL_LORA_OPERATION_SCOPE = DEFAULT_TRAINING_SCOPE
MAX_AUTHORIZATION_VALIDITY = timedelta(days=31)
ALLOWED_TRAINING_SCOPES = frozenset(
    {
        "validation_parameter_update",
        "production_training",
        "external_provider_training",
        "model_release",
        "deployment",
    }
)


class TrainingAuthorizationError(RuntimeError):
    """Raised when a v2 authorization is absent, invalid, or mismatched."""


@dataclass(frozen=True)
class ValidatedTrainingAuthorization:
    authorization_id: str
    decision: str
    authorized_scopes: List[str]
    required_scope: str
    dataset_version: str
    dataset_sha256: str
    registry_entry_id: str
    reviewer_id: str
    expires_at_utc: str
    key_id: str
    public_key_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "authorization_schema_version": AUTHORIZATION_SCHEMA_VERSION,
            "authorization_id": self.authorization_id,
            "decision": self.decision,
            "authorized_scopes": list(self.authorized_scopes),
            "required_scope": self.required_scope,
            "dataset_version": self.dataset_version,
            "dataset_sha256": self.dataset_sha256,
            "registry_entry_id": self.registry_entry_id,
            "reviewer_id": self.reviewer_id,
            "expires_at_utc": self.expires_at_utc,
            "authentication": {
                "algorithm": SIGNATURE_ALGORITHM,
                "key_id": self.key_id,
                "public_key_sha256": self.public_key_sha256,
                "verified": True,
            },
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_authorization_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TrainingAuthorizationError(f"authorization_file_not_found:{path}") from exc
    except json.JSONDecodeError as exc:
        raise TrainingAuthorizationError(f"authorization_json_invalid:{path}:{exc}") from exc
    if not isinstance(payload, dict):
        raise TrainingAuthorizationError("authorization_root_must_be_object")
    return payload


def canonical_authorization_bytes(payload: Dict[str, Any]) -> bytes:
    canonical_payload = copy.deepcopy(payload)
    authentication = canonical_payload.get("authentication")
    if not isinstance(authentication, dict):
        raise TrainingAuthorizationError("authorization.authentication_must_be_object")
    authentication.pop("value", None)
    return json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sign_training_authorization(
    payload: Dict[str, Any],
    private_key: Ed25519PrivateKey,
) -> Dict[str, Any]:
    signed = copy.deepcopy(payload)
    authentication = signed.get("authentication")
    if not isinstance(authentication, dict):
        raise TrainingAuthorizationError("authorization.authentication_must_be_object")
    authentication["public_key_sha256"] = private_key_public_sha256(private_key)
    authentication["value"] = sign_bytes(
        private_key,
        canonical_authorization_bytes(signed),
    )
    return signed


def build_training_authorization(
    *,
    authorization_id: str,
    decision: str,
    authorized_scopes: Iterable[str],
    dataset_version: str,
    dataset_sha256: str,
    registry_entry_id: str,
    reviewer_id: str,
    rationale: str,
    decision_source: str,
    key_id: str,
    issued_at: datetime,
    expires_at: datetime,
) -> Dict[str, Any]:
    if isinstance(authorized_scopes, (str, bytes)):
        raise TrainingAuthorizationError("authorized_scopes_must_be_array")
    scopes = _validate_scope_contract(decision, list(authorized_scopes))
    return {
        "authorization_schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "authorization_id": authorization_id,
        "decision": decision,
        "authorized_scopes": scopes,
        "dataset_binding": {
            "dataset_version": dataset_version,
            "dataset_sha256": dataset_sha256,
            "registry_entry_id": registry_entry_id,
        },
        "human_decision": {
            "reviewer_id": reviewer_id,
            "reviewed_at_utc": utc_iso(issued_at),
            "decision_source": decision_source,
            "rationale": rationale,
        },
        "validity": {
            "issued_at_utc": utc_iso(issued_at),
            "not_before_utc": utc_iso(issued_at),
            "expires_at_utc": utc_iso(expires_at),
        },
        "authentication": {
            "algorithm": SIGNATURE_ALGORITHM,
            "canonicalization": CANONICALIZATION_METHOD,
            "key_id": key_id,
            "public_key_sha256": "",
            "value": "",
        },
    }


def classify_legacy_fine_tuning_flags(
    values: Iterable[Optional[bool]],
) -> Dict[str, Any]:
    normalized = list(values)
    positive_count = sum(value is True for value in normalized)
    negative_count = sum(value is False for value in normalized)
    missing_count = len(normalized) - positive_count - negative_count
    return {
        "migration_outcome": "EXPLICIT_V2_AUTHORIZATION_REQUIRED",
        "automatic_scope_grant": False,
        "legacy_positive_count": positive_count,
        "legacy_negative_count": negative_count,
        "legacy_missing_count": missing_count,
        "rule": (
            "Legacy fine_tuning_allowed values are retained as historical evidence and "
            "shall not create a v2 authorization scope."
        ),
    }


def validate_training_authorization(
    payload: Dict[str, Any],
    *,
    public_key: Ed25519PublicKey,
    expected_dataset_version: str,
    expected_dataset_sha256: str,
    expected_registry_entry_id: str,
    required_scope: str,
    now: Optional[datetime] = None,
) -> ValidatedTrainingAuthorization:
    _require_exact_keys(
        payload,
        {
            "authorization_schema_version",
            "authorization_id",
            "decision",
            "authorized_scopes",
            "dataset_binding",
            "human_decision",
            "validity",
            "authentication",
        },
        "authorization",
    )
    version = _require_str(
        payload.get("authorization_schema_version"),
        "authorization_schema_version",
    )
    if version != AUTHORIZATION_SCHEMA_VERSION:
        raise TrainingAuthorizationError(
            f"authorization_schema_version_unsupported:{version}"
        )

    authorization_id = _require_str(payload.get("authorization_id"), "authorization_id")
    decision = _require_str(payload.get("decision"), "decision")
    if decision not in {"ALLOW", "DENY"}:
        raise TrainingAuthorizationError(f"authorization_decision_invalid:{decision}")

    scopes = _validate_scope_contract(decision, payload.get("authorized_scopes"))

    normalized_required_scope = _require_str(required_scope, "required_scope")
    if normalized_required_scope not in ALLOWED_TRAINING_SCOPES:
        raise TrainingAuthorizationError(
            f"required_scope_unknown:{normalized_required_scope}"
        )

    dataset_binding = _require_dict(payload.get("dataset_binding"), "dataset_binding")
    _require_exact_keys(
        dataset_binding,
        {"dataset_version", "dataset_sha256", "registry_entry_id"},
        "dataset_binding",
    )
    dataset_version = _require_str(
        dataset_binding.get("dataset_version"),
        "dataset_binding.dataset_version",
    )
    dataset_sha256 = _require_sha256(
        dataset_binding.get("dataset_sha256"),
        "dataset_binding.dataset_sha256",
    )
    registry_entry_id = _require_str(
        dataset_binding.get("registry_entry_id"),
        "dataset_binding.registry_entry_id",
    )
    if dataset_version != expected_dataset_version:
        raise TrainingAuthorizationError(
            "authorization_dataset_version_mismatch:"
            f"{dataset_version}!={expected_dataset_version}"
        )
    if dataset_sha256 != expected_dataset_sha256.lower():
        raise TrainingAuthorizationError(
            "authorization_dataset_sha256_mismatch:"
            f"{dataset_sha256}!={expected_dataset_sha256.lower()}"
        )
    if registry_entry_id != expected_registry_entry_id:
        raise TrainingAuthorizationError(
            "authorization_registry_entry_mismatch:"
            f"{registry_entry_id}!={expected_registry_entry_id}"
        )

    human_decision = _require_dict(payload.get("human_decision"), "human_decision")
    _require_exact_keys(
        human_decision,
        {"reviewer_id", "reviewed_at_utc", "decision_source", "rationale"},
        "human_decision",
    )
    reviewer_id = _require_str(
        human_decision.get("reviewer_id"),
        "human_decision.reviewer_id",
    )
    _require_str(human_decision.get("decision_source"), "human_decision.decision_source")
    rationale = _require_str(human_decision.get("rationale"), "human_decision.rationale")
    if len(rationale) < 20:
        raise TrainingAuthorizationError("human_decision.rationale_too_short")
    reviewed_at = _parse_utc(
        human_decision.get("reviewed_at_utc"),
        "human_decision.reviewed_at_utc",
    )

    validity = _require_dict(payload.get("validity"), "validity")
    _require_exact_keys(
        validity,
        {"issued_at_utc", "not_before_utc", "expires_at_utc"},
        "validity",
    )
    issued_at = _parse_utc(validity.get("issued_at_utc"), "validity.issued_at_utc")
    not_before = _parse_utc(
        validity.get("not_before_utc"),
        "validity.not_before_utc",
    )
    expires_at = _parse_utc(validity.get("expires_at_utc"), "validity.expires_at_utc")
    if reviewed_at != issued_at:
        raise TrainingAuthorizationError("reviewed_at_must_match_issued_at")
    if not_before < issued_at:
        raise TrainingAuthorizationError("authorization_not_before_precedes_issue")
    if expires_at <= not_before:
        raise TrainingAuthorizationError("authorization_expiry_must_follow_not_before")
    if expires_at - not_before > MAX_AUTHORIZATION_VALIDITY:
        raise TrainingAuthorizationError("authorization_validity_exceeds_31_days")
    effective_now = (now or utc_now()).astimezone(timezone.utc)
    if effective_now < not_before:
        raise TrainingAuthorizationError("authorization_not_yet_valid")
    if effective_now >= expires_at:
        raise TrainingAuthorizationError("authorization_expired")

    authentication = _require_dict(payload.get("authentication"), "authentication")
    _require_exact_keys(
        authentication,
        {
            "algorithm",
            "canonicalization",
            "key_id",
            "public_key_sha256",
            "value",
        },
        "authentication",
    )
    algorithm = _require_str(authentication.get("algorithm"), "authentication.algorithm")
    if algorithm != SIGNATURE_ALGORITHM:
        raise TrainingAuthorizationError(
            f"authentication_algorithm_unsupported:{algorithm}"
        )
    canonicalization = _require_str(
        authentication.get("canonicalization"),
        "authentication.canonicalization",
    )
    if canonicalization != CANONICALIZATION_METHOD:
        raise TrainingAuthorizationError(
            f"authentication_canonicalization_unsupported:{canonicalization}"
        )
    key_id = _require_str(authentication.get("key_id"), "authentication.key_id")
    recorded_fingerprint = _require_sha256(
        authentication.get("public_key_sha256"),
        "authentication.public_key_sha256",
    )
    trusted_fingerprint = public_key_sha256(public_key)
    if recorded_fingerprint != trusted_fingerprint:
        raise TrainingAuthorizationError(
            "authorization_public_key_mismatch:"
            f"{recorded_fingerprint}!={trusted_fingerprint}"
        )
    signature = _require_str(authentication.get("value"), "authentication.value")
    try:
        verify_bytes(public_key, canonical_authorization_bytes(payload), signature)
    except CryptoKeyError as exc:
        raise TrainingAuthorizationError(f"authorization_{exc}") from exc

    # A verified denial remains a denial; signatures do not grant permission.
    if decision != "ALLOW":
        raise TrainingAuthorizationError("authorization_decision_not_allow")
    if scopes != [normalized_required_scope]:
        raise TrainingAuthorizationError(
            f"authorization_scope_missing:{normalized_required_scope}"
        )

    return ValidatedTrainingAuthorization(
        authorization_id=authorization_id,
        decision=decision,
        authorized_scopes=scopes,
        required_scope=normalized_required_scope,
        dataset_version=dataset_version,
        dataset_sha256=dataset_sha256,
        registry_entry_id=registry_entry_id,
        reviewer_id=reviewer_id,
        expires_at_utc=utc_iso(expires_at),
        key_id=key_id,
        public_key_sha256=trusted_fingerprint,
    )


def require_local_lora_scope(requested_scope: str) -> str:
    """The reference runner implements research updates, not other operations."""
    scope = _require_str(requested_scope, "authorization_scope")
    if scope != LOCAL_LORA_OPERATION_SCOPE:
        raise TrainingAuthorizationError(
            f"endpoint_operation_scope_mismatch:{scope}!={LOCAL_LORA_OPERATION_SCOPE}"
        )
    return LOCAL_LORA_OPERATION_SCOPE


def _validate_scope_contract(decision: str, value: Any) -> List[str]:
    if decision not in {"ALLOW", "DENY"}:
        raise TrainingAuthorizationError(f"authorization_decision_invalid:{decision}")
    if not isinstance(value, list):
        raise TrainingAuthorizationError("authorized_scopes_must_be_array")
    if decision == "ALLOW" and len(value) != 1:
        raise TrainingAuthorizationError("allow_requires_exactly_one_scope")
    if decision == "DENY" and value:
        raise TrainingAuthorizationError("deny_authorization_must_not_include_scopes")
    scopes = [_require_str(scope, "authorized_scopes.item") for scope in value]
    if scopes != value:
        raise TrainingAuthorizationError("authorized_scopes_must_be_exact_identifiers")
    unknown = sorted(set(scopes) - ALLOWED_TRAINING_SCOPES)
    if unknown:
        raise TrainingAuthorizationError(f"authorized_scope_unknown:{','.join(unknown)}")
    return scopes


def _require_dict(value: Any, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TrainingAuthorizationError(f"{label}_must_be_object")
    return value


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrainingAuthorizationError(f"{label}_must_be_non_empty_string")
    return value.strip()


def _require_sha256(value: Any, label: str) -> str:
    normalized = _require_str(value, label).lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise TrainingAuthorizationError(f"{label}_must_be_sha256_hex")
    return normalized


def _require_exact_keys(value: Dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        raise TrainingAuthorizationError(f"{label}_missing_keys:{','.join(missing)}")
    if unexpected:
        raise TrainingAuthorizationError(
            f"{label}_unexpected_keys:{','.join(unexpected)}"
        )


def _parse_utc(value: Any, label: str) -> datetime:
    raw = _require_str(value, label)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TrainingAuthorizationError(f"{label}_must_be_iso8601") from exc
    if parsed.tzinfo is None:
        raise TrainingAuthorizationError(f"{label}_must_include_timezone")
    return parsed.astimezone(timezone.utc)
