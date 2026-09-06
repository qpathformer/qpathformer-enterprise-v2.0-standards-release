#!/usr/bin/env python3
"""Ed25519 key loading, generation, fingerprinting, signing, and verification."""

from __future__ import annotations

import base64
import binascii
import hashlib
import os
from pathlib import Path
from typing import Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


SIGNATURE_ALGORITHM = "Ed25519"
MIN_PRIVATE_KEY_PASSWORD_BYTES = 16


class CryptoKeyError(RuntimeError):
    """Raised when cryptographic key material is missing, invalid, or unsafe."""


def load_password_from_env(env_name: Optional[str]) -> Optional[bytes]:
    normalized_name = str(env_name or "").strip()
    if not normalized_name:
        return None
    raw_password = os.environ.get(normalized_name)
    if raw_password is None or not raw_password:
        raise CryptoKeyError(f"private_key_password_env_missing:{normalized_name}")
    password = raw_password.encode("utf-8")
    if len(password) < MIN_PRIVATE_KEY_PASSWORD_BYTES:
        raise CryptoKeyError(
            "private_key_password_too_short:"
            f"{len(password)}<{MIN_PRIVATE_KEY_PASSWORD_BYTES}"
        )
    return password


def load_ed25519_private_key(
    path: Path,
    *,
    password_env: Optional[str] = None,
) -> Ed25519PrivateKey:
    normalized_path = path.expanduser().resolve()
    try:
        key = serialization.load_pem_private_key(
            normalized_path.read_bytes(),
            password=load_password_from_env(password_env),
        )
    except FileNotFoundError as exc:
        raise CryptoKeyError(f"private_key_not_found:{normalized_path}") from exc
    except (TypeError, ValueError) as exc:
        raise CryptoKeyError(f"private_key_invalid:{normalized_path}") from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise CryptoKeyError(f"private_key_must_be_ed25519:{normalized_path}")
    return key


def load_ed25519_public_key(path: Path) -> Ed25519PublicKey:
    normalized_path = path.expanduser().resolve()
    try:
        key = serialization.load_pem_public_key(normalized_path.read_bytes())
    except FileNotFoundError as exc:
        raise CryptoKeyError(f"public_key_not_found:{normalized_path}") from exc
    except (TypeError, ValueError) as exc:
        raise CryptoKeyError(f"public_key_invalid:{normalized_path}") from exc
    if not isinstance(key, Ed25519PublicKey):
        raise CryptoKeyError(f"public_key_must_be_ed25519:{normalized_path}")
    return key


def public_key_sha256(public_key: Ed25519PublicKey) -> str:
    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return hashlib.sha256(raw_key).hexdigest()


def private_key_public_sha256(private_key: Ed25519PrivateKey) -> str:
    return public_key_sha256(private_key.public_key())


def sign_bytes(private_key: Ed25519PrivateKey, payload: bytes) -> str:
    return base64.b64encode(private_key.sign(payload)).decode("ascii")


def verify_bytes(
    public_key: Ed25519PublicKey,
    payload: bytes,
    signature_b64: str,
) -> None:
    try:
        signature = base64.b64decode(signature_b64.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        raise CryptoKeyError("signature_must_be_base64") from exc
    if len(signature) != 64:
        raise CryptoKeyError(f"ed25519_signature_length_invalid:{len(signature)}")
    try:
        public_key.verify(signature, payload)
    except InvalidSignature as exc:
        raise CryptoKeyError("ed25519_signature_verification_failed") from exc


def write_ed25519_keypair(
    *,
    private_key_path: Path,
    public_key_path: Path,
    password_env: Optional[str] = None,
) -> str:
    private_path = private_key_path.expanduser().resolve()
    public_path = public_key_path.expanduser().resolve()
    if private_path == public_path:
        raise CryptoKeyError("private_and_public_key_paths_must_differ")
    if private_path.exists():
        raise CryptoKeyError(f"private_key_output_already_exists:{private_path}")
    if public_path.exists():
        raise CryptoKeyError(f"public_key_output_already_exists:{public_path}")

    password = load_password_from_env(password_env)
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password is not None
        else serialization.NoEncryption()
    )
    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(private_bytes)
    public_path.write_bytes(public_bytes)
    return private_key_public_sha256(private_key)
