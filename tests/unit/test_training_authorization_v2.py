from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import migrate_training_package_authorization_v2 as migration  # noqa: E402
import run_state1_finetune_local_lora as finetune  # noqa: E402
import run_training_state1 as training_prep  # noqa: E402
from crypto_keys import (  # noqa: E402
    load_ed25519_private_key,
    load_ed25519_public_key,
    write_ed25519_keypair,
)
from package_sealing import (  # noqa: E402
    PACKAGE_SEAL_FILENAME,
    load_package_seal,
    validate_package_seal,
)
from training_authorization import (  # noqa: E402
    AUTHORIZATION_SCHEMA_VERSION,
    TrainingAuthorizationError,
    build_training_authorization,
    classify_legacy_fine_tuning_flags,
    sha256_file,
    sign_training_authorization,
    validate_training_authorization,
)


NOW = datetime.now(timezone.utc).replace(microsecond=0)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def create_keypair(root: Path, name: str) -> tuple[Path, Path]:
    private_path = root / "keys" / f"{name}.private.pem"
    public_path = root / "keys" / f"{name}.public.pem"
    write_ed25519_keypair(
        private_key_path=private_path,
        public_key_path=public_path,
    )
    return private_path, public_path


def legacy_candidate() -> dict:
    return {
        "candidate_id": "candidate-1",
        "source_signal_id": "signal-1",
        "source_state": "STATE_3",
        "target_model": {"parameter_class": "12B-14B", "role": "enterprise"},
        "transformation_type": "enterprise_structuring",
        "content": {"input": "Governed input", "output": "Governed output"},
        "authorization": {
            "status": "approved_for_candidate_use",
            "fine_tuning_allowed": False,
        },
        "review": {"status": "reviewed", "review_required": True},
        "routing": {
            "routing_decision": "SEND_TO_STATE_2_REVIEW",
            "eligible_for_state_2": True,
            "target_state": "STATE_2",
            "routing_reasons": ["review_ready"],
        },
        "validation": {
            "candidate_for_validation": True,
            "validation_requested": True,
            "validation_engine_version": "v2-test",
            "validation_reasons": ["validation_requested"],
        },
        "lineage": {
            "source_signal_ref": "signal-1",
            "transformation_id": "transform-1",
        },
        "timestamp": "2026-07-17T09:00:00Z",
    }


def backend_profile() -> dict:
    return {
        "backend_profile_version": "v14.3",
        "backend_profile_id": "local_lora_reference",
        "backend": "local_lora",
        "supported_backends": ["local_lora"],
        "compatible_package_states": ["STATE_1"],
        "format": "sft_jsonl",
        "prompt_field": "prompt",
        "completion_field": "completion",
        "include_metadata": True,
        "execution_mode": "configured",
        "model": {
            "model_base": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "model_family": "llama",
        },
        "default_hyperparameters": {
            "max_steps": 1,
            "learning_rate": 0.00005,
            "batch_size": 1,
        },
        "backend_config": {
            "device": "cpu",
            "seed": 42,
            "max_seq_len": 128,
            "num_train_epochs": 1.0,
            "gradient_accumulation_steps": 1,
            "warmup_steps": 0,
            "logging_steps": 1,
            "save_steps": 1,
            "save_total_limit": 1,
            "lora_r": 4,
            "lora_alpha": 8,
            "lora_dropout": 0.0,
            "target_modules": ["q_proj", "v_proj"],
            "fp16": False,
            "bf16": False,
            "gradient_checkpointing": False,
            "trust_remote_code": False,
        },
    }


def signed_authorization(
    dataset_path: Path,
    private_key_path: Path,
    *,
    dataset_version: str = "dataset-v2",
    registry_entry_id: str = "registry-entry-v2",
) -> dict:
    unsigned = build_training_authorization(
        authorization_id="QPAUTH-TEST-001",
        decision="ALLOW",
        authorized_scopes=["validation_parameter_update"],
        dataset_version=dataset_version,
        dataset_sha256=sha256_file(dataset_path),
        registry_entry_id=registry_entry_id,
        reviewer_id="reviewer-test",
        rationale="Explicit validation parameter update approval for the unit test dataset.",
        decision_source="unit_test_human_decision",
        key_id="authorization-test-key-v1",
        issued_at=NOW,
        expires_at=NOW + timedelta(days=7),
    )
    return sign_training_authorization(
        unsigned,
        load_ed25519_private_key(private_key_path),
    )


class TrainingAuthorizationV2Tests(unittest.TestCase):
    def test_ed25519_allow_validates_and_tampering_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            private_key_path, public_key_path = create_keypair(root, "authorization")
            _, wrong_public_key_path = create_keypair(root, "wrong-authorization")
            dataset_path = root / "dataset.jsonl"
            write_jsonl(dataset_path, [legacy_candidate()])
            payload = signed_authorization(dataset_path, private_key_path)

            validated = validate_training_authorization(
                payload,
                public_key=load_ed25519_public_key(public_key_path),
                expected_dataset_version="dataset-v2",
                expected_dataset_sha256=sha256_file(dataset_path),
                expected_registry_entry_id="registry-entry-v2",
                required_scope="validation_parameter_update",
                now=NOW + timedelta(hours=1),
            )
            self.assertEqual(validated.authorization_id, "QPAUTH-TEST-001")
            self.assertEqual(
                validated.to_dict()["authorization_schema_version"],
                AUTHORIZATION_SCHEMA_VERSION,
            )
            self.assertEqual(validated.to_dict()["authentication"]["algorithm"], "Ed25519")

            with self.assertRaisesRegex(
                TrainingAuthorizationError,
                "authorization_public_key_mismatch",
            ):
                validate_training_authorization(
                    payload,
                    public_key=load_ed25519_public_key(wrong_public_key_path),
                    expected_dataset_version="dataset-v2",
                    expected_dataset_sha256=sha256_file(dataset_path),
                    expected_registry_entry_id="registry-entry-v2",
                    required_scope="validation_parameter_update",
                    now=NOW + timedelta(hours=1),
                )

            payload["human_decision"]["rationale"] += " Tampered."
            with self.assertRaisesRegex(
                TrainingAuthorizationError,
                "authorization_ed25519_signature_verification_failed",
            ):
                validate_training_authorization(
                    payload,
                    public_key=load_ed25519_public_key(public_key_path),
                    expected_dataset_version="dataset-v2",
                    expected_dataset_sha256=sha256_file(dataset_path),
                    expected_registry_entry_id="registry-entry-v2",
                    required_scope="validation_parameter_update",
                    now=NOW + timedelta(hours=1),
                )

    def test_legacy_flags_never_create_v2_scope(self) -> None:
        migration_result = classify_legacy_fine_tuning_flags([True, False, None])
        self.assertEqual(
            migration_result["migration_outcome"],
            "EXPLICIT_V2_AUTHORIZATION_REQUIRED",
        )
        self.assertFalse(migration_result["automatic_scope_grant"])
        self.assertEqual(migration_result["legacy_positive_count"], 1)
        self.assertEqual(migration_result["legacy_negative_count"], 1)
        self.assertEqual(migration_result["legacy_missing_count"], 1)

    def test_legacy_package_migration_creates_authorized_sealed_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            auth_private, auth_public = create_keypair(root, "authorization")
            seal_private, seal_public = create_keypair(root, "package-seal")
            source_package = root / "legacy-package"
            source_dataset = source_package / "dataset.jsonl"
            write_jsonl(source_dataset, [legacy_candidate()])
            write_jsonl(
                source_package / "train.sft.jsonl",
                [{"prompt": "Governed input", "completion": "Governed output"}],
            )
            legacy_manifest = {
                "dataset_version": "dataset-v2",
                "lifecycle_state": "STATE_1",
                "record_count": 1,
                "train_file": "train.sft.jsonl",
                "registry_state": "STATE_1",
                "registry_entry_id": "registry-entry-v2",
                "target_model": {
                    "model_base": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                    "model_family": "llama",
                },
                "authorization_posture": {
                    "non_authoritative": True,
                    "governance_first": True,
                },
            }
            source_manifest_path = source_package / "state1_training_manifest.json"
            write_json(source_manifest_path, legacy_manifest)
            write_json(source_package / "training_backend_profile.json", backend_profile())
            source_manifest_bytes = source_manifest_path.read_bytes()
            authorization_path = root / "authorization.json"
            write_json(
                authorization_path,
                signed_authorization(source_dataset, auth_private),
            )
            output_root = root / "migrated"
            argv = [
                "migrate_training_package_authorization_v2.py",
                "--training-package",
                str(source_package),
                "--source-dataset",
                str(source_dataset),
                "--authorization-file",
                str(authorization_path),
                "--authorization-public-key",
                str(auth_public),
                "--package-seal-private-key",
                str(seal_private),
                "--package-seal-key-id",
                "package-seal-test-key-v1",
                "--output-root",
                str(output_root),
            ]
            with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                self.assertEqual(migration.main(), 0)

            migrated_package = output_root / "dataset-v2"
            self.assertEqual(source_manifest_path.read_bytes(), source_manifest_bytes)
            self.assertFalse((source_package / "training_authorization.json").exists())
            self.assertFalse((source_package / PACKAGE_SEAL_FILENAME).exists())
            self.assertTrue((migrated_package / "training_authorization.json").exists())
            self.assertTrue((migrated_package / PACKAGE_SEAL_FILENAME).exists())
            migrated_manifest = json.loads(
                (migrated_package / "state1_training_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                migrated_manifest["training_manifest_version"],
                "v12.2-migrated-auth-seal-v2",
            )
            self.assertFalse(
                migrated_manifest["authorization_migration"]["source_package_modified"]
            )

            seal_validation = validate_package_seal(
                load_package_seal(migrated_package / PACKAGE_SEAL_FILENAME),
                package_root=migrated_package,
                public_key=load_ed25519_public_key(seal_public),
                expected_dataset_version="dataset-v2",
                expected_registry_entry_id="registry-entry-v2",
            )
            self.assertGreaterEqual(seal_validation.file_count, 5)

            package_paths = finetune._resolve_training_package_paths(migrated_package)
            summary = finetune._validate_manifest_contract(migrated_manifest, package_paths)
            package_validation = finetune._validate_v2_package_seal(
                package_paths=package_paths,
                manifest_summary=summary,
                public_key_path=seal_public,
            )
            authorization_validation = finetune._validate_v2_training_authorization(
                package_paths=package_paths,
                manifest_summary=summary,
                required_scope="validation_parameter_update",
                public_key_path=auth_public,
            )
            self.assertTrue(package_validation["reverified_before_execution"])
            self.assertTrue(authorization_validation["reverified_before_execution"])

    def test_training_package_and_finetune_reverify_authorization_and_seal(self) -> None:
        self._assert_training_package_and_finetune_reverification()

    def test_training_package_dry_run_with_dotdot_temp_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir).resolve()
            alias = parent / ".." / parent.name
            self.assertNotEqual(str(alias), str(alias.resolve()))
            self._assert_training_package_and_finetune_reverification(temp_parent=alias)

    @unittest.skipUnless(sys.platform == "win32", "Windows short-name paths only")
    def test_training_package_dry_run_with_windows_short_temp_root(self) -> None:
        import ctypes

        get_short_path = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
        get_short_path.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        get_short_path.restype = ctypes.c_uint32
        with tempfile.TemporaryDirectory(prefix="qpath long temp root ") as temp_dir:
            parent = Path(temp_dir).resolve()
            size = get_short_path(str(parent), None, 0)
            if not size:
                self.skipTest("Windows short-name paths are unavailable")
            buffer = ctypes.create_unicode_buffer(size)
            written = get_short_path(str(parent), buffer, size)
            self.assertGreater(written, 0)
            self.assertLess(written, size)
            alias = Path(buffer.value)
            if str(alias) == str(parent):
                self.skipTest("No distinct Windows short-name alias is available")
            self.assertEqual(alias.resolve(), parent)
            self._assert_training_package_and_finetune_reverification(temp_parent=alias)

    def _assert_training_package_and_finetune_reverification(
        self, *, temp_parent: Path | None = None
    ) -> None:
        with tempfile.TemporaryDirectory(dir=temp_parent) as temp_dir:
            # Match the resolved roots used by the runtime, including Windows 8.3 aliases.
            root = Path(temp_dir).resolve()
            auth_private, auth_public = create_keypair(root, "authorization")
            seal_private, seal_public = create_keypair(root, "package-seal")
            dataset_version = "dataset-v2"
            registry_entry_id = "registry-entry-v2"
            freeze_dir = root / "source-package" / "freeze"
            dataset_path = freeze_dir / "frozen_dataset.jsonl"
            frozen_manifest_path = freeze_dir / "frozen_manifest.json"
            freeze_artifact_path = freeze_dir / "state1_freeze.json"
            write_jsonl(dataset_path, [legacy_candidate()])
            write_json(
                frozen_manifest_path,
                {
                    "dataset_version": dataset_version,
                    "state": "STATE_1",
                    "frozen_dataset_path": str(dataset_path),
                },
            )
            write_json(freeze_artifact_path, {"decision": {"approved": True}})
            registry_path = root / "state1_dataset_registry.json"
            write_json(
                registry_path,
                {
                    "registry_id": "registry-v2",
                    "created_at": "2026-07-17T09:00:00Z",
                    "updated_at": "2026-07-17T09:00:00Z",
                    "entries": [
                        {
                            "registry_entry_id": registry_entry_id,
                            "registered_at": "2026-07-17T09:00:00Z",
                            "state": "STATE_1",
                            "dataset_version": dataset_version,
                            "package_dir": str(freeze_dir.parent),
                            "freeze_dir": str(freeze_dir),
                            "frozen_manifest_path": str(frozen_manifest_path),
                            "freeze_artifact_path": str(freeze_artifact_path),
                        }
                    ],
                },
            )
            authorization_path = root / "authorization.json"
            write_json(
                authorization_path,
                signed_authorization(dataset_path, auth_private),
            )
            backend_profile_path = root / "backend_profile.json"
            write_json(backend_profile_path, backend_profile())
            training_output_root = root / "path_1" / "training_packages"

            prep_argv = [
                "run_training_state1.py",
                "--registry-path",
                str(registry_path),
                "--dataset-version",
                dataset_version,
                "--authorization-file",
                str(authorization_path),
                "--authorization-public-key",
                str(auth_public),
                "--package-seal-private-key",
                str(seal_private),
                "--package-seal-key-id",
                "package-seal-test-key-v1",
                "--output-root",
                str(training_output_root),
                "--backend-profile",
                str(backend_profile_path),
            ]
            with patch.object(sys, "argv", prep_argv), redirect_stdout(io.StringIO()):
                self.assertEqual(training_prep.main(), 0)

            training_package = training_output_root / dataset_version
            manifest = json.loads(
                (training_package / "state1_training_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["record_counts"]["exported_record_count"], 1)
            self.assertEqual(manifest["record_counts"]["fine_tuning_allowed_count"], 0)
            self.assertEqual(manifest["record_counts"]["v2_authorized_record_count"], 1)
            self.assertTrue(manifest["authorization_posture"]["v2_authorization_verified"])
            self.assertTrue(
                manifest["package_seal_posture"]["complete_package_seal_required"]
            )

            run_output_root = root / "runs"
            run_logs_root = root / "run_logs"
            run_profile = finetune.RunLogProfile(
                path_id="path_1_tr_corpus_reference",
                logs_root=run_logs_root,
                version_key="path1_run_log_version",
                output_key="path1_run_log",
                filename_prefix="path1_finetune_run_",
            )
            finetune_argv = [
                "run_state1_finetune_local_lora.py",
                "--training-package",
                str(training_package),
                "--authorization-public-key",
                str(auth_public),
                "--package-seal-public-key",
                str(seal_public),
                "--output-root",
                str(run_output_root),
                "--run-id",
                "authorized-sealed-dry-run",
                "--dry-run",
            ]
            with patch.object(finetune, "PATH1_ROOT", root / "path_1"):
                with patch.object(finetune, "PATH1_RUN_LOG_PROFILE", run_profile):
                    with (
                        patch.object(sys, "argv", finetune_argv),
                        patch.object(
                            finetune,
                            "_run_local_lora_training",
                            side_effect=AssertionError("Dry-run must not start model training"),
                        ),
                        redirect_stdout(io.StringIO()) as output,
                    ):
                        self.assertEqual(finetune.main(), 0, output.getvalue())
            run_manifest = json.loads(
                (
                    run_output_root
                    / "authorized-sealed-dry-run"
                    / "finetune_run_manifest.json"
                ).read_text(encoding="utf-8")
            )
            self.assertTrue(
                run_manifest["authorization_validation"]["reverified_before_execution"]
            )
            self.assertTrue(
                run_manifest["package_seal_validation"]["reverified_before_execution"]
            )

            train_path = training_package / "train.sft.jsonl"
            train_path.write_text(
                train_path.read_text(encoding="utf-8") + "{\"prompt\":\"tampered\"}\n",
                encoding="utf-8",
            )
            rejected_argv = [
                "run_state1_finetune_local_lora.py",
                "--training-package",
                str(training_package),
                "--authorization-public-key",
                str(auth_public),
                "--package-seal-public-key",
                str(seal_public),
                "--output-root",
                str(root / "rejected-runs"),
                "--run-id",
                "tampered-package-run",
                "--dry-run",
            ]
            with patch.object(sys, "argv", rejected_argv), redirect_stdout(io.StringIO()):
                self.assertEqual(finetune.main(), 1)
            self.assertFalse((root / "rejected-runs" / "tampered-package-run").exists())


if __name__ == "__main__":
    unittest.main()
