#!/usr/bin/env python3
"""Exercise the synthetic authorization boundary in an ephemeral script copy."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "crypto_keys.py", "package_sealing.py", "path_layout.py", "training_authorization.py",
    "generate_ed25519_keypair_v2.py", "create_training_authorization_v2.py",
    "run_training_state1.py", "run_state1_finetune_local_lora.py",
)
SCOPE = "validation_parameter_update"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def candidate(index):
    return {
        "candidate_id": f"synthetic-candidate-{index}", "source_signal_id": f"synthetic-signal-{index}",
        "source_state": "STATE_3", "target_model": {"parameter_class": "12B-14B", "role": "enterprise"},
        "transformation_type": "enterprise_structuring",
        "content": {"input": f"Synthetic input {index}", "output": "This is a synthetic example, not legal advice."},
        "authorization": {"status": "approved_for_candidate_use", "fine_tuning_allowed": False},
        "review": {"status": "reviewed", "review_required": True},
        "routing": {"routing_decision": "SEND_TO_STATE_2_REVIEW", "eligible_for_state_2": True,
                    "target_state": "STATE_2", "routing_reasons": ["synthetic_fixture"]},
        "validation": {"candidate_for_validation": True, "validation_requested": True,
                       "validation_engine_version": "synthetic", "validation_reasons": ["synthetic_fixture"]},
        "lineage": {"source_signal_ref": f"synthetic-signal-{index}", "transformation_id": "synthetic"},
        "timestamp": "2026-09-05T00:00:00Z",
    }


def rehearse(report):
    with tempfile.TemporaryDirectory(prefix="qpath standards rehearsal ") as temporary:
        workspace = Path(temporary).resolve()
        scripts = workspace / "scripts"
        scripts.mkdir()
        for name in SCRIPTS:
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        guard = workspace / "standards_rehearsal_child.py"
        shutil.copyfile(ROOT / "tools/standards_rehearsal_child.py", guard)
        report["source_files"] = {
            f"scripts/{name}": digest(scripts / name) for name in SCRIPTS
        }
        report["source_files"]["tools/standards_rehearsal_child.py"] = digest(guard)
        report["source_files"]["tools/rehearse_standards_release.py"] = digest(Path(__file__))
        profile_source = ROOT / "shared/configs/training_backend_profile.local_lora.json"
        profile = workspace / "profile.json"
        shutil.copyfile(profile_source, profile)
        report["source_files"]["shared/configs/training_backend_profile.local_lora.json"] = digest(profile)
        steps = report["steps"]

        def cli(name, args, expected=0, error=None):
            command = [sys.executable, "-B", str(guard), str(scripts / name), *map(str, args)]
            result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, timeout=60)
            text = result.stdout + result.stderr
            normalized = text.replace(str(workspace), "$WORKSPACE").replace(
                str(workspace).replace("\\", "\\\\"), "$WORKSPACE"
            )
            steps.append({
                "script": name,
                "arguments": [str(arg).replace(str(workspace), "$WORKSPACE") for arg in args],
                "exit_code": result.returncode, "expected_exit_code": expected,
                "expected_error": error, "output": normalized,
                "passed": result.returncode == expected and (error is None or error in text),
            })
            if not steps[-1]["passed"]:
                raise RuntimeError(f"rehearsal_step_failed:{name}:{normalized}")

        for role, prefix in [("authorization_signer", "auth"), ("package_sealer", "seal")]:
            cli("generate_ed25519_keypair_v2.py", [
                "--role", role, "--key-id", f"synthetic-{prefix}",
                "--private-key", workspace / f"{prefix}.private.pem",
                "--public-key", workspace / f"{prefix}.public.pem",
            ])

        version = "synthetic-standards-" + uuid4().hex
        entry_id = "synthetic-entry-" + uuid4().hex
        freeze = workspace / "synthetic-source" / "freeze"
        dataset = freeze / "frozen_dataset.jsonl"
        freeze.mkdir(parents=True)
        dataset.write_text("".join(json.dumps(candidate(i)) + "\n" for i in range(4)), encoding="utf-8")
        write_json(freeze / "frozen_manifest.json", {
            "dataset_version": version, "state": "STATE_1", "frozen_dataset_path": str(dataset),
        })
        write_json(freeze / "state1_freeze.json", {"decision": {"approved": True}, "synthetic_fixture": True})
        registry = workspace / "synthetic_registry.json"
        timestamp = datetime.now(timezone.utc).isoformat()
        write_json(registry, {
            "registry_id": "synthetic", "created_at": timestamp, "updated_at": timestamp,
            "entries": [{
                "registry_entry_id": entry_id, "registered_at": timestamp, "state": "STATE_1",
                "dataset_version": version, "package_dir": str(freeze.parent), "freeze_dir": str(freeze),
                "frozen_manifest_path": str(freeze / "frozen_manifest.json"),
                "freeze_artifact_path": str(freeze / "state1_freeze.json"),
            }],
        })
        registry_before = digest(registry)
        dataset_before = digest(dataset)
        auth = workspace / "synthetic_authorization.json"
        auth_args = [
            "--dataset-version", version, "--dataset-path", dataset, "--registry-entry-id", entry_id,
            "--decision", "ALLOW", "--scope", SCOPE, "--reviewer-id", "SYNTHETIC-NOT-A-LAWYER",
            "--decision-source", "synthetic_rehearsal_fixture",
            "--rationale", "Synthetic test decision only; no real legal review or operational approval.",
            "--key-id", "synthetic-auth", "--private-key", workspace / "auth.private.pem",
            "--acknowledge-human-decision", "--output", auth,
        ]
        cli("create_training_authorization_v2.py", auth_args)
        multiple = auth_args[:-1] + [workspace / "must-not-exist" / "multi.json", "--scope", "production_training"]
        cli("create_training_authorization_v2.py", multiple, expected=1, error="allow_requires_exactly_one_scope")
        if (workspace / "must-not-exist").exists():
            raise RuntimeError("invalid_authorization_created_output")
        output = workspace / "path_1_tr_corpus_reference" / "03_dataset" / "training_packages"
        prep_args = [
            "--registry-path", registry, "--dataset-version", version,
            "--authorization-file", auth, "--authorization-public-key", workspace / "auth.public.pem",
            "--authorization-scope", SCOPE, "--package-seal-private-key", workspace / "seal.private.pem",
            "--package-seal-key-id", "synthetic-seal", "--backend-profile", profile, "--output-root", output,
        ]
        cli("run_training_state1.py", prep_args)
        package = output / version
        package_before = {p.name: digest(p) for p in package.iterdir() if p.is_file()}
        runs = workspace / "runs"
        run_args = [
            "--training-package", package, "--authorization-public-key", workspace / "auth.public.pem",
            "--package-seal-public-key", workspace / "seal.public.pem", "--authorization-scope", SCOPE,
            "--output-root", runs, "--run-id", "synthetic-valid", "--dry-run",
        ]
        cli("run_state1_finetune_local_lora.py", run_args)
        manifest = json.loads((runs / "synthetic-valid" / "finetune_run_manifest.json").read_text())
        if manifest.get("dry_run") is not True:
            raise RuntimeError("rehearsal_dry_run_not_recorded")
        report["artifact_hashes"] = {
            "package_before_tamper": package_before,
            "valid_run": {
                p.relative_to(runs / "synthetic-valid").as_posix(): digest(p)
                for p in (runs / "synthetic-valid").rglob("*") if p.is_file()
            },
        }
        wrong_args = list(run_args)
        wrong_args[wrong_args.index("--authorization-scope") + 1] = "model_release"
        wrong_args[wrong_args.index("--run-id") + 1] = "synthetic-wrong-operation"
        cli("run_state1_finetune_local_lora.py", wrong_args, expected=1, error="endpoint_operation_scope_mismatch")
        unsupported = workspace / "unsupported-location" / version
        shutil.copytree(package, unsupported)
        route_args = list(run_args)
        route_args[route_args.index("--training-package") + 1] = unsupported
        route_args[route_args.index("--run-id") + 1] = "synthetic-wrong-route"
        cli("run_state1_finetune_local_lora.py", route_args, expected=1,
            error="unsupported_training_package_path_for_top_level_run_log")
        with (package / "train.sft.jsonl").open("a", encoding="utf-8") as handle:
            handle.write('{"prompt":"deliberately tampered synthetic fixture"}\n')
        tampered = list(run_args)
        tampered[tampered.index("--run-id") + 1] = "synthetic-tampered"
        cli("run_state1_finetune_local_lora.py", tampered, expected=1, error="package_inventory_verification_failed")
        rejected = ["synthetic-wrong-operation", "synthetic-wrong-route", "synthetic-tampered"]
        if any((runs / name).exists() for name in rejected):
            raise RuntimeError("rejected_operation_created_run_directory")
        if digest(registry) != registry_before or digest(dataset) != dataset_before:
            raise RuntimeError("synthetic_source_or_registry_modified")
        report["checks"] = {
            "source_dataset_unchanged": True, "synthetic_registry_unchanged": True,
            "rejected_run_directories_absent": True, "temporary_keys_only": True,
            "model_import_and_socket_connection_guard_enabled": True,
        }
    report["temporary_workspace_removed"] = True
    report["status"] = "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path, help="New report path; existing files are not overwritten.")
    args = parser.parse_args()
    report_path = args.report.expanduser().resolve()
    if report_path.exists():
        parser.error("report_already_exists")
    report = {
        "status": "FAIL", "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "synthetic_authorization_boundary_only",
        "python": sys.version.split()[0], "platform": platform.platform(),
        "steps": [], "real_training": False, "real_legal_review": False,
        "limits": [
            "Synthetic STATE_1/registry fixtures are inputs, not a replay of all three lifecycle paths.",
            "No real rights permission, professional qualification or organization delegation is verified.",
            "No hosted CI, model-quality, production, CSC-score or publication claim.",
            "Temporary keys are disposable test identities, not operational trust anchors.",
        ],
    }
    try:
        rehearse(report)
    except Exception as exc:
        report["error"] = str(exc)
    write_json(report_path, report)
    print(json.dumps({"status": report["status"], "report": str(report_path), "steps": len(report["steps"])}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
