from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

from crypto_keys import (  # noqa: E402
    load_ed25519_private_key,
    load_ed25519_public_key,
    write_ed25519_keypair,
)
from package_sealing import (  # noqa: E402
    PACKAGE_SEAL_FILENAME,
    PackageSealError,
    build_package_inventory,
    calculate_merkle_root,
    load_package_seal,
    validate_package_seal,
    write_package_seal,
)


def create_keypair(root: Path, name: str) -> tuple[Path, Path]:
    private_path = root / "keys" / f"{name}.private.pem"
    public_path = root / "keys" / f"{name}.public.pem"
    write_ed25519_keypair(
        private_key_path=private_path,
        public_key_path=public_path,
    )
    return private_path, public_path


def create_package(root: Path) -> Path:
    package = root / "package"
    (package / "nested").mkdir(parents=True)
    (package / "train.sft.jsonl").write_text(
        '{"prompt":"a","completion":"b"}\n',
        encoding="utf-8",
    )
    (package / "state1_training_manifest.json").write_text(
        json.dumps(
            {
                "dataset_version": "dataset-v2",
                "registry_entry_id": "registry-entry-v2",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (package / "nested" / "profile.json").write_text("{}\n", encoding="utf-8")
    return package


class PackageSealingV2Tests(unittest.TestCase):
    def test_inventory_and_merkle_root_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = create_package(Path(temp_dir))
            first = build_package_inventory(package)
            second = build_package_inventory(package)
            self.assertEqual(first, second)
            self.assertEqual(calculate_merkle_root(first), calculate_merkle_root(second))
            self.assertEqual(
                [entry["path"] for entry in first],
                [
                    "nested/profile.json",
                    "state1_training_manifest.json",
                    "train.sft.jsonl",
                ],
            )

    def test_signed_seal_validates_and_wrong_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            private_path, public_path = create_keypair(root, "seal")
            _, wrong_public_path = create_keypair(root, "wrong")
            package = create_package(root)
            write_package_seal(
                package_root=package,
                dataset_version="dataset-v2",
                registry_entry_id="registry-entry-v2",
                key_id="seal-key-v1",
                private_key=load_ed25519_private_key(private_path),
            )
            validated = validate_package_seal(
                load_package_seal(package / PACKAGE_SEAL_FILENAME),
                package_root=package,
                public_key=load_ed25519_public_key(public_path),
                expected_dataset_version="dataset-v2",
                expected_registry_entry_id="registry-entry-v2",
            )
            self.assertEqual(validated.file_count, 3)
            with self.assertRaisesRegex(PackageSealError, "package_seal_public_key_mismatch"):
                validate_package_seal(
                    load_package_seal(package / PACKAGE_SEAL_FILENAME),
                    package_root=package,
                    public_key=load_ed25519_public_key(wrong_public_path),
                    expected_dataset_version="dataset-v2",
                    expected_registry_entry_id="registry-entry-v2",
                )

    def test_manifest_binding_must_match_seal_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            private_path, _ = create_keypair(root, "seal")
            package = create_package(root)
            with self.assertRaisesRegex(
                PackageSealError,
                "training_manifest_dataset_version_mismatch",
            ):
                write_package_seal(
                    package_root=package,
                    dataset_version="different-dataset",
                    registry_entry_id="registry-entry-v2",
                    key_id="seal-key-v1",
                    private_key=load_ed25519_private_key(private_path),
                )

    def test_changed_added_and_removed_files_fail_inventory_verification(self) -> None:
        mutations = ("changed", "added", "removed")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                private_path, public_path = create_keypair(root, "seal")
                package = create_package(root)
                write_package_seal(
                    package_root=package,
                    dataset_version="dataset-v2",
                    registry_entry_id="registry-entry-v2",
                    key_id="seal-key-v1",
                    private_key=load_ed25519_private_key(private_path),
                )
                if mutation == "changed":
                    (package / "train.sft.jsonl").write_text("tampered\n", encoding="utf-8")
                elif mutation == "added":
                    (package / "added.txt").write_text("added\n", encoding="utf-8")
                else:
                    (package / "nested" / "profile.json").unlink()
                with self.assertRaisesRegex(
                    PackageSealError,
                    "package_inventory_verification_failed",
                ):
                    validate_package_seal(
                        load_package_seal(package / PACKAGE_SEAL_FILENAME),
                        package_root=package,
                        public_key=load_ed25519_public_key(public_path),
                        expected_dataset_version="dataset-v2",
                        expected_registry_entry_id="registry-entry-v2",
                    )

    def test_signed_seal_metadata_tampering_fails_signature_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            private_path, public_path = create_keypair(root, "seal")
            package = create_package(root)
            write_package_seal(
                package_root=package,
                dataset_version="dataset-v2",
                registry_entry_id="registry-entry-v2",
                key_id="seal-key-v1",
                private_key=load_ed25519_private_key(private_path),
            )
            payload = copy.deepcopy(load_package_seal(package / PACKAGE_SEAL_FILENAME))
            payload["created_at_utc"] = "2026-07-18T00:00:00Z"
            (package / PACKAGE_SEAL_FILENAME).write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                PackageSealError,
                "package_seal_ed25519_signature_verification_failed",
            ):
                validate_package_seal(
                    payload,
                    package_root=package,
                    public_key=load_ed25519_public_key(public_path),
                    expected_dataset_version="dataset-v2",
                    expected_registry_entry_id="registry-entry-v2",
                )


if __name__ == "__main__":
    unittest.main()
