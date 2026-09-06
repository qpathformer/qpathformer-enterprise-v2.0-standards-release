from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

from test_training_authorization_v2 import (
    NOW, REPO_ROOT, backend_profile, create_keypair, legacy_candidate,
    signed_authorization, write_json, write_jsonl,
)

import create_training_authorization_v2 as creator
import migrate_training_package_authorization_v2 as migration
import run_state1_finetune_local_lora as finetune
import run_training_state1 as preparation
from crypto_keys import load_ed25519_private_key, load_ed25519_public_key
from package_sealing import PACKAGE_SEAL_FILENAME, write_package_seal
from training_authorization import (
    AUTHORIZATION_SCHEMA_VERSION, TrainingAuthorizationError,
    build_training_authorization, sha256_file, sign_training_authorization,
    utc_iso, validate_training_authorization,
)


SCOPE = "validation_parameter_update"


def invoke(module, argv):
    with patch.object(sys, "argv", [module.__file__, *map(str, argv)]):
        with redirect_stdout(io.StringIO()) as output:
            status = module.main()
    return status, output.getvalue()


class SingleScopeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.auth_private, self.auth_public = create_keypair(self.root, "authorization")
        self.seal_private, self.seal_public = create_keypair(self.root, "seal")
        self.dataset = self.root / "source" / "freeze" / "frozen_dataset.jsonl"
        write_jsonl(self.dataset, [legacy_candidate()])
        self.payload = signed_authorization(self.dataset, self.auth_private)

    def sign(self, payload):
        return sign_training_authorization(payload, load_ed25519_private_key(self.auth_private))

    def validate(self, payload, *, now=NOW, **kwargs):
        return validate_training_authorization(
            payload, public_key=load_ed25519_public_key(self.auth_public),
            expected_dataset_version="dataset-v2",
            expected_dataset_sha256=sha256_file(self.dataset),
            expected_registry_entry_id="registry-entry-v2",
            required_scope=kwargs.get("required_scope", SCOPE), now=now,
        )

    def test_builder_rejects_implicit_multiple_and_invalid_scopes(self):
        for decision, scopes in [
            ("ALLOW", []), ("ALLOW", [SCOPE, "production_training"]),
            ("ALLOW", [SCOPE, SCOPE]), ("ALLOW", ["unknown"]),
            ("ALLOW", [" " + SCOPE]), ("DENY", [SCOPE]), ("MAYBE", []),
        ]:
            with self.subTest(decision=decision, scopes=scopes):
                with self.assertRaises(TrainingAuthorizationError):
                    build_training_authorization(
                        authorization_id="synthetic", decision=decision,
                        authorized_scopes=scopes, dataset_version="dataset-v2",
                        dataset_sha256=sha256_file(self.dataset),
                        registry_entry_id="registry-entry-v2", reviewer_id="synthetic",
                        rationale="Synthetic contract rejection test only.",
                        decision_source="synthetic", key_id="synthetic",
                        issued_at=NOW, expires_at=NOW + timedelta(hours=1),
                    )

    def test_schema_and_verifier_agree_on_scope_and_version_rejection(self):
        schema = json.loads((REPO_ROOT / "shared/schemas/authorization/training_authorization_v2.schema.json").read_text())
        validator = Draft202012Validator(schema)
        validator.validate(self.payload)
        variants = [
            ("authorized_scopes", []),
            ("authorized_scopes", [SCOPE, "production_training"]),
            ("authorized_scopes", [SCOPE, SCOPE]),
            ("authorized_scopes", ["unknown"]),
            ("authorization_schema_version", "qpath_training_authorization_v2.1"),
        ]
        for key, value in variants:
            with self.subTest(key=key, value=value):
                payload = copy.deepcopy(self.payload)
                payload[key] = value
                payload = self.sign(payload)
                self.assertTrue(list(validator.iter_errors(payload)))
                with self.assertRaises(TrainingAuthorizationError):
                    self.validate(payload)

    def test_signed_deny_has_no_scope_and_never_authorizes(self):
        payload = copy.deepcopy(self.payload)
        payload["decision"] = "DENY"
        payload["authorized_scopes"] = []
        with self.assertRaisesRegex(TrainingAuthorizationError, "authorization_decision_not_allow"):
            self.validate(self.sign(payload))
        payload["authorized_scopes"] = [SCOPE]
        with self.assertRaisesRegex(TrainingAuthorizationError, "deny_authorization_must_not_include_scopes"):
            self.validate(self.sign(payload))

    def test_validity_boundaries_are_inclusive_start_exclusive_expiry(self):
        start = NOW + timedelta(hours=1)
        end = NOW + timedelta(hours=2)
        payload = copy.deepcopy(self.payload)
        payload["validity"]["not_before_utc"] = utc_iso(start)
        payload["validity"]["expires_at_utc"] = utc_iso(end)
        payload = self.sign(payload)
        self.assertEqual(self.validate(payload, now=start).authorized_scopes, [SCOPE])
        self.validate(payload, now=end - timedelta(microseconds=1))
        for now, error in [
            (start - timedelta(microseconds=1), "authorization_not_yet_valid"),
            (end, "authorization_expired"),
        ]:
            with self.subTest(now=now):
                with self.assertRaisesRegex(TrainingAuthorizationError, error):
                    self.validate(payload, now=now)

    def test_signed_dataset_binding_mismatches_fail(self):
        for field, value, error in [
            ("dataset_version", "other-version", "authorization_dataset_version_mismatch"),
            ("dataset_sha256", "0" * 64, "authorization_dataset_sha256_mismatch"),
            ("registry_entry_id", "other-entry", "authorization_registry_entry_mismatch"),
        ]:
            with self.subTest(field=field):
                payload = copy.deepcopy(self.payload)
                payload["dataset_binding"][field] = value
                with self.assertRaisesRegex(TrainingAuthorizationError, error):
                    self.validate(self.sign(payload))

    def creator_args(self, output):
        return [
            "--dataset-version", "dataset-v2", "--dataset-path", self.dataset,
            "--registry-entry-id", "registry-entry-v2", "--decision", "ALLOW",
            "--reviewer-id", "synthetic-reviewer", "--decision-source", "synthetic",
            "--rationale", "Synthetic verification, no real human or legal permission.",
            "--key-id", "synthetic", "--private-key", self.auth_private,
            "--acknowledge-human-decision", "--output", output,
        ]

    def test_creator_requires_one_explicit_scope_without_writes_on_rejection(self):
        for extra in [[], ["--scope", SCOPE, "--scope", SCOPE],
                      ["--scope", SCOPE, "--scope", "production_training"]]:
            output = self.root / "rejected" / "authorization.json"
            status, text = invoke(creator, self.creator_args(output) + extra)
            self.assertEqual(status, 1, text)
            self.assertIn("allow_requires_exactly_one_scope", text)
            self.assertFalse(output.parent.exists())
        output = self.root / "valid" / "authorization.json"
        status, text = invoke(creator, self.creator_args(output) + ["--scope", SCOPE])
        self.assertEqual(status, 0, text)
        payload = json.loads(output.read_text())
        self.assertEqual(payload["authorization_schema_version"], AUTHORIZATION_SCHEMA_VERSION)
        self.assertEqual(payload["authorized_scopes"], [SCOPE])

    def prep_args(self, scope=SCOPE):
        freeze = self.dataset.parent
        write_json(freeze / "frozen_manifest.json", {
            "dataset_version": "dataset-v2", "state": "STATE_1",
            "frozen_dataset_path": str(self.dataset),
        })
        write_json(freeze / "state1_freeze.json", {"decision": {"approved": True}})
        registry = self.root / "registry.json"
        write_json(registry, {
            "registry_id": "synthetic", "created_at": utc_iso(NOW), "updated_at": utc_iso(NOW),
            "entries": [{
                "registry_entry_id": "registry-entry-v2", "registered_at": utc_iso(NOW),
                "state": "STATE_1", "dataset_version": "dataset-v2",
                "package_dir": str(freeze.parent), "freeze_dir": str(freeze),
                "frozen_manifest_path": str(freeze / "frozen_manifest.json"),
                "freeze_artifact_path": str(freeze / "state1_freeze.json"),
            }],
        })
        write_json(self.root / "authorization.json", self.payload)
        write_json(self.root / "backend.json", backend_profile())
        return [
            "--registry-path", registry, "--dataset-version", "dataset-v2",
            "--authorization-file", self.root / "authorization.json",
            "--authorization-public-key", self.auth_public, "--authorization-scope", scope,
            "--package-seal-private-key", self.seal_private, "--package-seal-key-id", "synthetic-seal",
            "--backend-profile", self.root / "backend.json",
            "--output-root", self.root / "packages",
        ]

    def package(self):
        status, text = invoke(preparation, self.prep_args())
        self.assertEqual(status, 0, text)
        return self.root / "packages" / "dataset-v2"

    def run_args(self, package, scope=SCOPE):
        return [
            "--training-package", package, "--authorization-public-key", self.auth_public,
            "--package-seal-public-key", self.seal_public, "--authorization-scope", scope,
            "--output-root", self.root / "runs", "--run-id", "synthetic-rejected", "--dry-run",
        ]

    def assert_runner_rejected(self, package, *, scope=SCOPE, error):
        with patch.object(finetune, "_execute_backend") as backend:
            status, text = invoke(finetune, self.run_args(package, scope))
        self.assertEqual(status, 1, text)
        self.assertIn(error, text)
        backend.assert_not_called()
        self.assertFalse((self.root / "runs").exists())

    def test_preparation_rejects_other_operations_before_registry_access(self):
        for scope in ["production_training", "external_provider_training", "model_release", "deployment"]:
            with self.subTest(scope=scope), patch.object(preparation, "_load_json") as load:
                status, text = invoke(preparation, self.prep_args(scope))
                self.assertEqual(status, 1, text)
                self.assertIn("endpoint_operation_scope_mismatch", text)
                load.assert_not_called()
                self.assertFalse((self.root / "packages").exists())

    def test_runner_rejects_relabelled_operation_before_package_access(self):
        for scope in ["production_training", "external_provider_training", "model_release", "deployment"]:
            with self.subTest(scope=scope), patch.object(finetune, "_resolve_training_package_paths") as resolve:
                self.assert_runner_rejected(
                    self.root / "not-read", scope=scope, error="endpoint_operation_scope_mismatch",
                )
                resolve.assert_not_called()

    def test_legacy_authorization_is_not_automatically_migrated_or_written(self):
        self.payload["authorization_schema_version"] = "qpath_training_authorization_v2.1"
        self.payload = self.sign(self.payload)
        original = copy.deepcopy(self.payload)
        status, text = invoke(preparation, self.prep_args())
        self.assertEqual(status, 1, text)
        self.assertIn("authorization_schema_version_unsupported", text)
        self.assertEqual(json.loads((self.root / "authorization.json").read_text()), original)
        self.assertFalse((self.root / "packages").exists())

    def test_migration_cannot_relabel_operation(self):
        argv = [
            "--training-package", self.root / "missing",
            "--source-dataset", self.dataset, "--authorization-file", self.root / "missing.json",
            "--authorization-public-key", self.auth_public, "--output-root", self.root / "migrated",
            "--authorization-scope", "model_release", "--package-seal-private-key", self.seal_private,
            "--package-seal-key-id", "synthetic",
        ]
        status, text = invoke(migration, argv)
        self.assertEqual(status, 1, text)
        self.assertIn("endpoint_operation_scope_mismatch", text)
        self.assertFalse((self.root / "migrated").exists())

    def test_shared_authorization_and_seal_key_rejected_without_outputs(self):
        self.seal_private = self.auth_private
        status, text = invoke(preparation, self.prep_args())
        self.assertEqual(status, 1, text)
        self.assertIn("authorization_and_package_seal_keys_must_be_distinct", text)
        self.assertFalse((self.root / "packages").exists())

    def test_unsupported_log_route_leaves_no_run_directory(self):
        package = self.package()
        self.assert_runner_rejected(package, error="unsupported_training_package_path_for_top_level_run_log")

    def test_validly_sealed_wrong_scope_is_rejected_for_research_runner(self):
        package = self.package()
        manifest_path = package / "state1_training_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        payload = copy.deepcopy(self.payload)
        payload["authorized_scopes"] = ["production_training"]
        write_json(package / "training_authorization.json", self.sign(payload))
        posture = manifest["authorization_posture"]
        posture["authorized_scope"] = "production_training"
        posture["authorized_scopes"] = ["production_training"]
        posture["authorization_artifact_sha256"] = sha256_file(package / "training_authorization.json")
        write_json(manifest_path, manifest)
        (package / PACKAGE_SEAL_FILENAME).unlink()
        write_package_seal(
            package_root=package, dataset_version="dataset-v2", registry_entry_id="registry-entry-v2",
            key_id="synthetic-seal", private_key=load_ed25519_private_key(self.seal_private),
        )
        self.assert_runner_rejected(package, error="authorization_scope_manifest_mismatch")
        self.assert_runner_rejected(package, scope="production_training", error="endpoint_operation_scope_mismatch")

    def test_sealed_denied_expired_and_mismatched_records_never_enter_backend(self):
        package = self.package()
        manifest_path = package / "state1_training_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        for variant, error in [
            ("denied", "authorization_decision_not_allow"),
            ("expired", "authorization_expired"),
            ("not_before", "authorization_not_yet_valid"),
            ("registry", "authorization_registry_entry_mismatch"),
            ("dataset", "authorization_dataset_sha256_mismatch"),
        ]:
            with self.subTest(variant=variant):
                payload = copy.deepcopy(self.payload)
                if variant == "denied":
                    payload["decision"] = "DENY"
                    payload["authorized_scopes"] = []
                elif variant == "expired":
                    issued = NOW - timedelta(days=2)
                    payload["human_decision"]["reviewed_at_utc"] = utc_iso(issued)
                    payload["validity"] = {
                        "issued_at_utc": utc_iso(issued), "not_before_utc": utc_iso(issued),
                        "expires_at_utc": utc_iso(NOW - timedelta(days=1)),
                    }
                elif variant == "not_before":
                    payload["validity"]["not_before_utc"] = utc_iso(NOW + timedelta(days=1))
                elif variant == "registry":
                    payload["dataset_binding"]["registry_entry_id"] = "other-entry"
                else:
                    payload["dataset_binding"]["dataset_sha256"] = "0" * 64
                write_json(package / "training_authorization.json", self.sign(payload))
                manifest["authorization_posture"]["authorization_artifact_sha256"] = sha256_file(
                    package / "training_authorization.json"
                )
                write_json(manifest_path, manifest)
                (package / PACKAGE_SEAL_FILENAME).unlink()
                write_package_seal(
                    package_root=package, dataset_version="dataset-v2",
                    registry_entry_id="registry-entry-v2", key_id="synthetic-seal",
                    private_key=load_ed25519_private_key(self.seal_private),
                )
                self.assert_runner_rejected(package, error=error)

    def test_isolated_cli_rehearsal_records_nine_expected_outcomes(self):
        report = self.root / "rehearsal.json"
        result = subprocess.run(
            [sys.executable, "-B", str(REPO_ROOT / "tools/rehearse_standards_release.py"),
             "--report", str(report)], capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(report.read_text())
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(len(payload["steps"]), 9)
        self.assertTrue(all(step["passed"] for step in payload["steps"]))
        self.assertTrue(payload["temporary_workspace_removed"])
        self.assertFalse(payload["real_training"])
        self.assertFalse(payload["real_legal_review"])


if __name__ == "__main__":
    unittest.main()
