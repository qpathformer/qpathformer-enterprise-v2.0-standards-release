#!/usr/bin/env python3
"""Validate the portable Q-Pathformer Enterprise v2 release tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


EXPECTED_RELEASE_LOCK = [
    "attrs==26.1.0",
    "cffi==2.1.0",
    "cryptography==49.0.0",
    "jsonschema==4.26.0",
    "jsonschema-specifications==2025.9.1",
    "pycparser==3.0",
    "referencing==0.37.0",
    "rpds-py==0.30.0",
]

REQUIRED_FILES = [
    ".github/workflows/release-validation.yml",
    "LICENSE",
    "QPATHFORMER-PLATFORM-1.0.txt",
    "README.md",
    "REPOSITORY_MANIFEST.json",
    "SOURCE_PROVENANCE.json",
    "docs/README.md",
    "docs/REPOSITORY_LAYOUT.md",
    "docs/execution/REPRODUCIBILITY.md",
    "docs/release/AI_ASSISTED_DEVELOPMENT_DISCLOSURE.md",
    "docs/release/TR010_RELEASE_BOUNDARY.md",
    "docs/release/V2_CSC_GOVERNANCE_SNAPSHOT_AND_SCORING_CONTRACT.md",
    "release/DOCUMENTATION_CONFORMANCE_REPORT.json",
    "release/EXCLUSIONS.json",
    "release/MODEL_AND_DERIVATIVE_ASSET_MANIFEST.json",
    "release/THIRD_PARTY_NOTICES.md",
    "release/V1_CSC_EVIDENCE_MANIFEST.json",
    "release/V1_GIT_SOURCE_ANCHOR.json",
    "release/V1_STANDARDS_VENDOR_VERIFICATION.json",
    "release/V2_CSC_GOVERNANCE_SNAPSHOT_CONTRACT.json",
    "requirements-release.txt",
    "scripts/validate_v2_release.py",
]

REQUIRED_DIRECTORIES = [
    "docs/architecture",
    "docs/execution",
    "docs/orientation/results_docs",
    "docs/release",
    "path_1_tr_corpus_reference/01_source",
    "path_1_tr_corpus_reference/02_signals",
    "path_1_tr_corpus_reference/03_dataset/checkpoint_v4_strict",
    "path_1_tr_corpus_reference/04_state1_package",
    "path_1_tr_corpus_reference/05_runs",
    "path_1_tr_corpus_reference/07_logs",
    "path_2_access_mode_canonical/01_source",
    "path_2_access_mode_canonical/02_signals",
    "path_2_access_mode_canonical/03_dataset",
    "path_2_access_mode_canonical/05_runs",
    "path_2_access_mode_canonical/07_logs",
    "path_3_external_custom_adapter/01_source",
    "path_3_external_custom_adapter/03_dataset",
    "path_3_external_custom_adapter/07_logs",
    "planning/migration",
    "planning/optimization",
    "release",
    "scripts/runtime",
    "shared/configs",
    "shared/models/evaluation",
    "shared/models/qpathformer",
    "shared/registry/examples",
    "shared/runtime/signal_references",
    "shared/schemas/authorization",
    "shared/standards/access_pod",
    "tests/unit",
]

PROHIBITED_ROOTS = [
    "_upstream_qpath-dataset-lifecycle",
    "legacy_reference",
    "tests/fixtures",
]

PROHIBITED_MODEL_EXTENSIONS = {
    ".bin",
    ".ckpt",
    ".gguf",
    ".onnx",
    ".pt",
    ".pth",
    ".safetensors",
}

ACTIVE_TEXT_ROOTS = [
    "README.md",
    "REPOSITORY_MANIFEST.json",
    "SOURCE_PROVENANCE.json",
    "docs/README.md",
    "docs/REPOSITORY_LAYOUT.md",
    "docs/architecture/minimal_three_path_root_structure.md",
    "docs/execution",
    "docs/release",
    "release/EXCLUSIONS.json",
    "release/MODEL_AND_DERIVATIVE_ASSET_MANIFEST.json",
    "release/THIRD_PARTY_NOTICES.md",
    "release/V1_GIT_SOURCE_ANCHOR.json",
    "release/V1_STANDARDS_VENDOR_VERIFICATION.json",
    "release/V2_CSC_GOVERNANCE_SNAPSHOT_CONTRACT.json",
]

SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def active_text_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for item in ACTIVE_TEXT_ROOTS:
        path = root / item
        if path.is_file():
            files.add(path)
        elif path.is_dir():
            files.update(p for p in path.rglob("*") if p.is_file())
    return sorted(files)


def extract_link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0] if raw else ""


def validate(root: Path, allow_missing_report: bool) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(check_id: str, passed: bool, details: object) -> None:
        checks.append(
            {
                "check_id": check_id,
                "status": "PASS" if passed else "FAIL",
                "details": details,
            }
        )

    missing_files = [
        item
        for item in REQUIRED_FILES
        if not (root / item).is_file()
        and not (allow_missing_report and item == "release/DOCUMENTATION_CONFORMANCE_REPORT.json")
    ]
    add("required_files", not missing_files, {"missing": missing_files})

    missing_directories = [
        item for item in REQUIRED_DIRECTORIES if not (root / item).is_dir()
    ]
    add(
        "required_directories",
        not missing_directories,
        {"missing": missing_directories},
    )

    prohibited = [item for item in PROHIBITED_ROOTS if (root / item).exists()]
    add("prohibited_roots", not prohibited, {"present": prohibited})

    generated_caches = [
        relative(path, root)
        for path in root.rglob("*")
        if "__pycache__" in path.parts
        or ".pytest_cache" in path.parts
        or path.suffix.lower() in {".pyc", ".pyo"}
    ]
    add(
        "generated_cache_exclusion",
        not generated_caches,
        {"paths": sorted(set(generated_caches))},
    )

    reparse_points = []
    for path in root.rglob("*"):
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
        if path.is_symlink() or attributes & 0x400:
            reparse_points.append(relative(path, root))
    add(
        "symlinks_and_reparse_links",
        not reparse_points,
        {"paths": reparse_points},
    )

    lock_path = root / "requirements-release.txt"
    actual_lock = []
    if lock_path.is_file():
        actual_lock = [
            line.strip()
            for line in lock_path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    add(
        "exact_release_dependency_lock",
        actual_lock == EXPECTED_RELEASE_LOCK,
        {"expected": EXPECTED_RELEASE_LOCK, "actual": actual_lock},
    )

    invalid_json: list[dict[str, str]] = []
    json_files = list(root.rglob("*.json"))
    for path in json_files:
        try:
            read_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            invalid_json.append({"path": relative(path, root), "error": str(exc)})
    add(
        "json_syntax",
        not invalid_json,
        {"checked": len(json_files), "invalid": invalid_json},
    )

    invalid_jsonl: list[dict[str, object]] = []
    jsonl_files = list(root.rglob("*.jsonl"))
    jsonl_record_count = 0
    for path in jsonl_files:
        try:
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8-sig").splitlines(), start=1
            ):
                if not line.strip():
                    continue
                jsonl_record_count += 1
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    invalid_jsonl.append(
                        {
                            "path": relative(path, root),
                            "line": line_number,
                            "error": str(exc),
                        }
                    )
        except (OSError, UnicodeError) as exc:
            invalid_jsonl.append({"path": relative(path, root), "error": str(exc)})
    add(
        "jsonl_syntax",
        not invalid_jsonl,
        {
            "checked_files": len(jsonl_files),
            "checked_records": jsonl_record_count,
            "invalid": invalid_jsonl,
        },
    )

    markdown_files = list(root.rglob("*.md"))
    heading_failures: list[dict[str, object]] = []
    link_failures: list[dict[str, object]] = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        lines = text.splitlines()
        if not any(line.startswith("# ") for line in lines):
            heading_failures.append(
                {"path": relative(path, root), "reason": "missing_H1"}
            )
        for line_number, line in enumerate(lines, start=1):
            if re.match(r"^\s*\\#+\s", line):
                heading_failures.append(
                    {
                        "path": relative(path, root),
                        "line": line_number,
                        "reason": "escaped_heading",
                    }
                )
        for match in MARKDOWN_LINK.finditer(text):
            target = unquote(extract_link_target(match.group(1)))
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if target.startswith("/") or WINDOWS_ABSOLUTE_PATH.search(target):
                link_failures.append(
                    {
                        "path": relative(path, root),
                        "target": target,
                        "reason": "absolute_local_link",
                    }
                )
                continue
            candidate = (path.parent / target.replace("\\", os.sep)).resolve()
            if not candidate.exists():
                link_failures.append(
                    {
                        "path": relative(path, root),
                        "target": target,
                        "reason": "missing_target",
                    }
                )
    add(
        "markdown_headings",
        not heading_failures,
        {"checked": len(markdown_files), "failures": heading_failures},
    )
    add(
        "markdown_internal_links",
        not link_failures,
        {"failures": link_failures},
    )

    active_paths = active_text_files(root)
    absolute_path_findings: list[dict[str, object]] = []
    for path in active_paths:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if WINDOWS_ABSOLUTE_PATH.search(line) or "file:///" in line.lower():
                absolute_path_findings.append(
                    {"path": relative(path, root), "line": line_number}
                )
    add(
        "active_local_absolute_paths",
        not absolute_path_findings,
        {
            "checked": len(active_paths),
            "findings": absolute_path_findings,
            "historical_metadata_policy": "Inert historical paths outside the active set are preserved and excluded from this check.",
        },
    )

    secret_findings: list[dict[str, str]] = []
    text_extensions = {
        ".json",
        ".jsonl",
        ".md",
        ".ps1",
        ".py",
        ".txt",
        ".yml",
        ".yaml",
    }
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_extensions:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                secret_findings.append({"path": relative(path, root), "pattern": name})
    private_key_files = [
        relative(path, root)
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".key", ".p12", ".pem", ".pfx"}
    ]
    add(
        "secret_scan",
        not secret_findings and not private_key_files,
        {"findings": secret_findings, "private_key_files": private_key_files},
    )

    all_files = [path for path in root.rglob("*") if path.is_file()]
    oversized = [
        {"path": relative(path, root), "bytes": path.stat().st_size}
        for path in all_files
        if path.stat().st_size > 10 * 1024 * 1024
    ]
    add(
        "file_size_limit",
        not oversized,
        {"limit_bytes": 10 * 1024 * 1024, "oversized": oversized},
    )

    model_assets = [
        relative(path, root)
        for path in all_files
        if path.suffix.lower() in PROHIBITED_MODEL_EXTENSIONS
    ]
    add("model_binary_exclusion", not model_assets, {"paths": model_assets})

    licence_paths = [
        "LICENSE",
        "QPATHFORMER-PLATFORM-1.0.txt",
        "release/THIRD_PARTY_NOTICES.md",
        "shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/LICENSE",
        "shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/ORIGIN.md",
    ]
    missing_licences = [item for item in licence_paths if not (root / item).is_file()]
    add("licence_and_notice_files", not missing_licences, {"missing": missing_licences})

    layout_text = (root / "docs/REPOSITORY_LAYOUT.md").read_text(
        encoding="utf-8-sig", errors="replace"
    ) if (root / "docs/REPOSITORY_LAYOUT.md").is_file() else ""
    layout_tokens = [
        "docs/",
        "path_1_tr_corpus_reference/",
        "path_2_access_mode_canonical/",
        "path_3_external_custom_adapter/",
        "planning/",
        "release/",
        "scripts/",
        "shared/",
        "tests/",
    ]
    readme_path = root / "README.md"
    readme_text = readme_path.read_text(
        encoding="utf-8-sig", errors="replace"
    ) if readme_path.is_file() else ""
    missing_layout_tokens = [token for token in layout_tokens if token not in layout_text]
    missing_readme_tokens = [token for token in layout_tokens if token not in readme_text]
    missing_tree_roots = [
        token for token in layout_tokens if not (root / token.rstrip("/")).is_dir()
    ]
    add(
        "repository_layout_document",
        not missing_layout_tokens and not missing_readme_tokens and not missing_tree_roots,
        {
            "missing_documented_roots": missing_layout_tokens,
            "missing_readme_roots": missing_readme_tokens,
            "missing_target_roots": missing_tree_roots,
        },
    )

    path3_failures: list[str] = []
    path3_reconciliation_path = root / (
        "planning/migration/V1_PATH3_PROVENANCE_RECONCILIATION.json"
    )
    path3_publication_path = root / "planning/migration/V2_PUBLICATION_DECISIONS.md"
    path3_external_doc_path = root / (
        "docs/execution/path_3_external_custom_adapter_commands.md"
    )
    path3_client_doc_path = root / (
        "docs/execution/path_3_client_custom_dataset_commands.md"
    )
    path3_quick_prompts_path = root / "docs/execution/three_path_quick_prompts.md"
    excluded_path3_roots = [
        "path_3_external_custom_adapter/01_source/inbound/QPDS-PACKAGE-001",
        "path_3_external_custom_adapter/03_dataset/normalized/QPDS-PACKAGE-001",
        "path_3_external_custom_adapter/07_logs/onboarding_logs/QPDS-PACKAGE-001",
    ]
    for item in excluded_path3_roots:
        if (root / item).exists():
            path3_failures.append(f"excluded_positive_evidence_present:{item}")
    client_input = root / (
        "path_3_external_custom_adapter/01_source/inbound/"
        "CLIENT-DATASET-EXAMPLE-001/client_governance.json"
    )
    client_report = root / (
        "path_3_external_custom_adapter/03_dataset/normalized/"
        "CLIENT-DATASET-EXAMPLE-001/hash_verification_report.json"
    )
    if not client_input.is_file():
        path3_failures.append("selected_client_input_missing")
    if not client_report.is_file():
        path3_failures.append("selected_client_hash_report_missing")
    else:
        report = read_json(client_report)
        if report.get("overall_status") != "ok":
            path3_failures.append("selected_client_hash_status_not_ok")
    if not path3_reconciliation_path.is_file():
        path3_failures.append("M03_reconciliation_missing")
    else:
        reconciliation = read_json(path3_reconciliation_path)
        if reconciliation.get("result") != "PASS":
            path3_failures.append("M03_reconciliation_not_PASS")
        decision = reconciliation.get("decision", "").lower()
        if "exclude the bundle" not in decision or "do not rewrite" not in decision:
            path3_failures.append("M03_exclusion_decision_drift")
    publication_text = path3_publication_path.read_text(
        encoding="utf-8-sig", errors="replace"
    ).lower() if path3_publication_path.is_file() else ""
    for term in [
        "excluded from positive release evidence",
        "only the validated `client-dataset-example-001`",
    ]:
        if term not in publication_text:
            path3_failures.append(f"publication_decision_term_missing:{term}")
    external_doc = path3_external_doc_path.read_text(
        encoding="utf-8-sig", errors="replace"
    ).lower() if path3_external_doc_path.is_file() else ""
    external_doc = " ".join(external_doc.split())
    for term in [
        "not included as positive v2 evidence",
        "reviewer supplies a separate governed bundle",
        "do not run the commands in this file against `qpds-package-001`",
    ]:
        if term not in external_doc:
            path3_failures.append(f"external_doc_boundary_missing:{term}")
    client_doc = path3_client_doc_path.read_text(
        encoding="utf-8-sig", errors="replace"
    ).lower() if path3_client_doc_path.is_file() else ""
    client_doc = " ".join(client_doc.split())
    if "only populated path 3 input" not in client_doc:
        path3_failures.append("client_doc_selected_input_boundary_missing")
    quick_prompts = path3_quick_prompts_path.read_text(
        encoding="utf-8-sig", errors="replace"
    ).lower() if path3_quick_prompts_path.is_file() else ""
    quick_prompts = " ".join(quick_prompts.split())
    if "then the populated path 3 client-json route" not in quick_prompts:
        path3_failures.append("full_three_path_prompt_uses_unpopulated_route")
    add(
        "path3_m03_publication_treatment",
        not path3_failures,
        {
            "failures": path3_failures,
            "selected_populated_example": "CLIENT-DATASET-EXAMPLE-001",
            "excluded_positive_evidence": "QPDS-PACKAGE-001",
        },
    )

    mutable_or_training_state_paths = [
        "shared/registry/run_registry.json",
        "shared/registry/run_registry.legacy_20260413.json",
        "shared/registry/state1_dataset_registry.json",
        "shared/registry/run_references",
    ]
    mutable_state_present = [
        item for item in mutable_or_training_state_paths if (root / item).exists()
    ]
    optimizer_or_checkpoint_files = [
        relative(path, root)
        for path in all_files
        if re.search(r"(?i)(optimizer|checkpoint|adapter_model)", path.name)
        and path.suffix.lower() not in {".json", ".md", ".py", ".txt"}
    ]
    add(
        "mutable_registry_and_training_state_exclusion",
        not mutable_state_present and not optimizer_or_checkpoint_files,
        {
            "mutable_registry_paths": mutable_state_present,
            "optimizer_checkpoint_or_adapter_files": optimizer_or_checkpoint_files,
            "historical_registry_update_receipts": "allowed immutable path evidence",
        },
    )

    vendor_failures: list[str] = []
    verification_path = root / "release/V1_STANDARDS_VENDOR_VERIFICATION.json"
    manifest_path = root / (
        "shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/"
        "manifest_v1a_pack.json"
    )
    if verification_path.is_file() and manifest_path.is_file():
        verification = read_json(verification_path)
        manifest = read_json(manifest_path)
        recorded = {
            entry["relative_path"]: entry for entry in verification.get("entries", [])
        }
        statuses: list[str] = []
        vendor_root = manifest_path.parent
        for entry in manifest.get("files", []):
            rel = entry["relative_path"].replace("\\", "/")
            record = recorded.get(rel)
            if record is None:
                vendor_failures.append(f"missing_record:{rel}")
                continue
            actual_path = vendor_root / rel
            if not actual_path.is_file():
                vendor_failures.append(f"missing_file:{rel}")
                continue
            actual_bytes = actual_path.stat().st_size
            actual_hash = sha256_file(actual_path)
            raw_bytes = actual_path.read_bytes()
            byte_match = actual_bytes == entry["bytes"] and actual_hash == entry["sha256"]
            canonical_bytes = raw_bytes.replace(b"\r\n", b"\n")
            canonical_hash = hashlib.sha256(canonical_bytes).hexdigest()
            canonical_match = (
                len(canonical_bytes) == entry["bytes"]
                and canonical_hash == entry["sha256"]
            )
            expected_status = "BYTE_MATCH" if byte_match else "CANONICAL_LF_MATCH" if canonical_match else "FAIL"
            statuses.append(expected_status)
            comparisons = {
                "manifest_bytes": entry["bytes"],
                "physical_bytes": actual_bytes,
                "manifest_sha256": entry["sha256"],
                "physical_sha256": actual_hash,
                "verification_status": expected_status,
            }
            for key, value in comparisons.items():
                if record.get(key) != value:
                    vendor_failures.append(f"record_drift:{rel}:{key}")
            if expected_status == "CANONICAL_LF_MATCH":
                canonical_comparisons = {
                    "crlf_sequence_count": raw_bytes.count(b"\r\n"),
                    "canonical_bytes": len(canonical_bytes),
                    "canonical_sha256": canonical_hash,
                    "canonicalization": "CRLF_TO_LF",
                }
                for key, value in canonical_comparisons.items():
                    if record.get(key) != value:
                        vendor_failures.append(f"canonical_record_drift:{rel}:{key}")
            elif expected_status == "BYTE_MATCH" and record.get("canonicalization") != "none":
                vendor_failures.append(f"unexpected_canonicalization:{rel}")
        if statuses.count("BYTE_MATCH") != 3 or statuses.count("CANONICAL_LF_MATCH") != 6:
            vendor_failures.append("unexpected_manifest_match_profile")
        if "FAIL" in statuses:
            vendor_failures.append("unresolved_vendor_entry")
        if verification.get("verification_outcome") != "PASS_CANONICAL_EQUIVALENCE":
            vendor_failures.append("verification_outcome_drift")
        if verification.get("release_treatment") != "ACCEPTED_CANONICAL_EQUIVALENCE":
            vendor_failures.append("release_treatment_drift")
    else:
        vendor_failures.append("vendor_verification_inputs_missing")
    add(
        "vendor_manifest_verification_and_disclosure",
        not vendor_failures,
        {
            "failures": vendor_failures,
            "expected_profile": {"byte_matches": 3, "canonical_lf_matches": 6},
            "release_treatment": "ACCEPTED_CANONICAL_EQUIVALENCE",
        },
    )

    contract_failures: list[str] = []
    contract_path = root / "release/V2_CSC_GOVERNANCE_SNAPSHOT_CONTRACT.json"
    contract_doc_path = root / "docs/release/V2_CSC_GOVERNANCE_SNAPSHOT_AND_SCORING_CONTRACT.md"
    if contract_path.is_file() and contract_doc_path.is_file():
        contract = read_json(contract_path)
        if contract.get("status") != "DESIGN_BASELINE_NOT_YET_ENFORCED":
            contract_failures.append("unexpected_contract_status")
        if contract.get("active_v2_scoring_enabled") is not False:
            contract_failures.append("active_scoring_must_be_false")
        if contract.get("historical_non_retroactivity") is not True:
            contract_failures.append("historical_non_retroactivity_missing")
        statuses = set(contract.get("observation_status", {}).get("allowed", []))
        expected_statuses = {
            "observed",
            "insufficient_evidence",
            "unobserved",
            "not_applicable",
            "suspended",
        }
        if statuses != expected_statuses:
            contract_failures.append("observation_status_set_drift")
        if contract.get("observation_status", {}).get("numeric_value_allowed_for") != ["observed"]:
            contract_failures.append("numeric_value_rule_drift")
        if contract.get("cross_version_policy", {}).get("implicit_blending_allowed") is not False:
            contract_failures.append("implicit_blending_must_be_false")
        if contract.get("level_cap_policy", {}).get("status") != "CALIBRATION_REQUIRED_NOT_ACTIVE":
            contract_failures.append("level_cap_policy_must_fail_closed")
        layers = contract.get("layers", [])
        if len(layers) != 4:
            contract_failures.append("unexpected_layer_count")
        for layer in layers:
            for artifact in layer.get("artifacts", []):
                artifact_path = root / artifact.get("path", "")
                if not artifact_path.is_file():
                    contract_failures.append(f"missing_bound_artifact:{artifact.get('path')}")
                elif sha256_file(artifact_path) != artifact.get("sha256"):
                    contract_failures.append(f"bound_artifact_hash_mismatch:{artifact.get('path')}")
        contract_doc = contract_doc_path.read_text(encoding="utf-8-sig").lower()
        for term in [
            "not activate a new scorer",
            "missing observations are never imputed as zero",
            "implicit cross-version",
            "does not yet enforce",
        ]:
            if term not in contract_doc:
                contract_failures.append(f"contract_document_term_missing:{term}")
    else:
        contract_failures.append("governance_contract_files_missing")
    add(
        "v2_governance_snapshot_and_scoring_contract",
        not contract_failures,
        {"failures": contract_failures, "enforcement_status": "not_implemented"},
    )

    csc_failures: list[str] = []
    csc_path = root / "release/V1_CSC_EVIDENCE_MANIFEST.json"
    if csc_path.is_file():
        csc = read_json(csc_path)
        items = csc.get("items", [])
        if csc.get("gate_result") != "PASS":
            csc_failures.append("M08_gate_result_not_PASS")
        if csc.get("profile_count") != 4 or csc.get("selected_item_count") != 25:
            csc_failures.append("unexpected_profile_or_item_count")
        if len(items) != 25:
            csc_failures.append("item_list_count_mismatch")
        expected_path2_run = (
            "RTRUN-llm-runtime-registration-check-20260413T095208Z-77a538bc"
        )
        required_item_fields = [
            "profile_role",
            "generation_path",
            "confidence_or_provisionality",
            "sector_validation_status",
            "qualification_text",
            "v2_regeneration_statement",
        ]
        for item in items:
            item_path = root / item["target_relative_path"]
            if not item_path.is_file():
                csc_failures.append(f"missing_item:{item['item_id']}")
                continue
            if item_path.stat().st_size != item["byte_size"]:
                csc_failures.append(f"byte_size_mismatch:{item['item_id']}")
            if sha256_file(item_path) != item["sha256"]:
                csc_failures.append(f"hash_mismatch:{item['item_id']}")
            if item.get("not_regenerated_under_v2") is not True:
                csc_failures.append(f"v2_boundary_missing:{item['item_id']}")
            if item.get("v1_tag_byte_match") is not True:
                csc_failures.append(f"v1_tag_binding_missing:{item['item_id']}")
            for field in required_item_fields:
                if not item.get(field):
                    csc_failures.append(
                        f"qualification_field_missing:{item['item_id']}:{field}"
                    )
            if item.get("catalog_metric_count") != 60:
                csc_failures.append(f"catalogue_count_drift:{item['item_id']}")
            if item.get("observed_metric_count") not in {12, 16}:
                csc_failures.append(f"observed_count_drift:{item['item_id']}")
            provenance = item.get("path2_session_or_run_provenance", {})
            if provenance.get("path_id") != "path_2_access_mode_canonical":
                csc_failures.append(f"path2_origin_missing:{item['item_id']}")
            if provenance.get("run_id") != expected_path2_run:
                csc_failures.append(f"path2_run_id_drift:{item['item_id']}")
            if not provenance.get("run_at") or not provenance.get("origin_statement"):
                csc_failures.append(f"path2_provenance_incomplete:{item['item_id']}")
        profiles = csc.get("profile_summaries", [])
        if len(profiles) != 4:
            csc_failures.append("profile_summary_count_mismatch")
        for profile in profiles:
            if profile.get("path2_run_id") != expected_path2_run:
                csc_failures.append(
                    f"profile_path2_run_id_drift:{profile.get('profile_id')}"
                )
            for field in [
                "profile_role",
                "generation_path",
                "confidence_or_provisionality",
                "sector_validation_status",
                "qualification_text",
            ]:
                if not profile.get(field):
                    csc_failures.append(
                        f"profile_qualification_missing:{profile.get('profile_id')}:{field}"
                    )
    else:
        csc_failures.append("M08_manifest_missing")
    add("qualified_v1_csc_evidence", not csc_failures, {"failures": csc_failures})

    disclosure_path = root / "docs/release/AI_ASSISTED_DEVELOPMENT_DISCLOSURE.md"
    disclosure = disclosure_path.read_text(encoding="utf-8-sig").lower() if disclosure_path.is_file() else ""
    disclosure_terms = [
        "codex",
        "chatgpt",
        "human release authority",
        "independently tested",
        "no governance authority",
        "no assurance authority",
        "no release authority",
    ]
    missing_disclosure_terms = [term for term in disclosure_terms if term not in disclosure]
    add(
        "ai_assistance_disclosure",
        not missing_disclosure_terms,
        {"missing_terms": missing_disclosure_terms},
    )

    boundary_path = root / "docs/release/TR010_RELEASE_BOUNDARY.md"
    boundary = boundary_path.read_text(encoding="utf-8-sig").lower() if boundary_path.is_file() else ""
    boundary_terms = [
        "does not claim",
        "not model-quality proof",
        "not yet",
        "human release authority",
    ]
    missing_boundary_terms = [term for term in boundary_terms if term not in boundary]
    add(
        "release_claim_boundary",
        not missing_boundary_terms,
        {"missing_terms": missing_boundary_terms},
    )

    passed = all(check["status"] == "PASS" for check in checks)
    resolved_conditions = [
        {
            "id": "V1_VENDOR_CANONICAL_EQUIVALENCE",
            "record": "release/V1_STANDARDS_VENDOR_VERIFICATION.json",
            "status": "RESOLVED",
            "reason": "Three files are byte-exact and six reproduce the manifest exactly after the approved CRLF-to-LF canonical transform.",
        }
    ]
    return {
        "document_id": "QPATH-V2-M10-RELEASE-CONFORMANCE-001",
        "version": "3.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "validation_result": "PASS" if passed else "FAIL",
        "release_gate_recommendation": "PASS" if passed else "FAIL",
        "root": ".",
        "file_count_at_validation": len(all_files),
        "byte_count_at_validation": sum(path.stat().st_size for path in all_files),
        "check_count": len(checks),
        "passed_check_count": sum(check["status"] == "PASS" for check in checks),
        "failed_check_count": sum(check["status"] == "FAIL" for check in checks),
        "checks": checks,
        "known_holds": [],
        "resolved_conditions": resolved_conditions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    parser.add_argument(
        "--report-output",
        help="Write the JSON conformance report to this repository-relative path.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate without writing a report; requires the existing report record.",
    )
    args = parser.parse_args()
    if args.check_only and args.report_output:
        parser.error("--check-only and --report-output are mutually exclusive")
    return args


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps({"status": "error", "reason": "root_not_found"}))
        return 2

    report = validate(root, allow_missing_report=bool(args.report_output))
    if args.report_output:
        output = (root / args.report_output).resolve()
        try:
            output.relative_to(root)
        except ValueError:
            print(json.dumps({"status": "error", "reason": "report_outside_root"}))
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["validation_result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
