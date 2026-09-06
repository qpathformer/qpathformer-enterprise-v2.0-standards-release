from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

from run_state1_freeze import State1Freezer  # noqa: E402
from run_state1_handoff import State1HandoffBuilder  # noqa: E402
from run_state1_registry_update import State1RegistryUpdater  # noqa: E402
from run_state2_promotion import State2PromotionEvaluator  # noqa: E402
from run_state2_review import State2Reviewer  # noqa: E402


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def candidate(candidate_id: str, *, maturity: str | None = "LEVEL_4") -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "candidate_id": candidate_id,
        "content": {"input": "input", "output": "output"},
        "routing": {
            "eligible_for_state_2": True,
            "routing_decision": "SEND_TO_STATE_2_REVIEW",
            "target_state": "STATE_2",
        },
        "validation": {
            "candidate_for_validation": True,
            "validation_requested": True,
        },
    }
    if maturity is not None:
        row["review_metadata"] = {"maturity": maturity}
    return row


def create_review_package(
    root: Path,
    name: str,
    *,
    maturity: str | None,
    created_at: str,
) -> Path:
    package_dir = root / name
    write_json(
        package_dir / "manifest.json",
        {
            "dataset_version": name,
            "created_at": created_at,
            "source_record_count": 1,
        },
    )
    write_jsonl(package_dir / "dataset.jsonl", [candidate(f"{name}-1", maturity=maturity)])
    return package_dir


def create_lifecycle_package(
    root: Path,
    name: str,
    *,
    review_approved: bool,
    review_timestamp: str,
    promotion_approved: bool | None = None,
    promotion_timestamp: str | None = None,
) -> Path:
    package_dir = root / name
    rows = [candidate(f"{name}-{index}") for index in range(4)]
    write_json(
        package_dir / "manifest.json",
        {
            "dataset_version": name,
            "candidate_count": 4,
            "source_record_count": 4,
        },
    )
    write_jsonl(package_dir / "dataset.jsonl", rows)
    write_json(
        package_dir / "state2_review.json",
        {
            "review_timestamp": review_timestamp,
            "decision": {
                "approved": review_approved,
                "decision": (
                    "ELIGIBLE_FOR_HUMAN_REVIEW"
                    if review_approved
                    else "INSUFFICIENT_EVIDENCE"
                ),
            },
            "review_metrics": {
                "review_ready_count": 4,
                "review_ready_ratio": 1.0,
                "routing_mismatch_count": 0,
                "missing_content_count": 0,
            },
            "exceptions": {},
        },
    )
    if promotion_approved is not None:
        write_json(
            package_dir / "state2_promotion_decision.json",
            {
                "promotion_timestamp": promotion_timestamp,
                "decision": {
                    "approved": promotion_approved,
                    "decision": (
                        "APPROVE_STATE1_PROMOTION_CANDIDATE"
                        if promotion_approved
                        else "HOLD_STATE2_PACKAGE"
                    ),
                },
                "promotion_metrics": {"review_ready_ratio": 1.0},
            },
        )
    return package_dir


class FailClosedLifecycleTests(unittest.TestCase):
    def test_missing_maturity_is_insufficient_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = create_review_package(
                Path(temp_dir),
                "missing-maturity",
                maturity=None,
                created_at="2026-07-17T12:00:00Z",
            )
            reviewer = State2Reviewer(
                package_dir=package_dir,
                latest_root=None,
                min_candidates=1,
                min_review_ready_ratio=1.0,
                min_level4_ratio=1.0,
                dry_run=False,
                notes=None,
            )

            result = reviewer.run()

            self.assertFalse(result["decision"]["approved"])
            self.assertEqual(result["decision"]["decision"], "INSUFFICIENT_EVIDENCE")
            self.assertEqual(result["review_metrics"]["level4_or_higher_ratio"], 0.0)
            self.assertEqual(
                result["exceptions"]["missing_maturity_candidate_ids"],
                ["missing-maturity-1"],
            )
            self.assertTrue((package_dir / "state2_review.json").exists())

    def test_latest_review_skips_newer_held_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            newer = create_review_package(
                root,
                "newer-held",
                maturity=None,
                created_at="2026-07-17T12:00:00Z",
            )
            older = create_review_package(
                root,
                "older-eligible",
                maturity="LEVEL_4",
                created_at="2026-07-17T11:00:00Z",
            )
            reviewer = State2Reviewer(
                package_dir=None,
                latest_root=root,
                min_candidates=1,
                min_review_ready_ratio=1.0,
                min_level4_ratio=1.0,
                dry_run=False,
                notes=None,
            )

            result = reviewer.run()

            self.assertTrue(result["decision"]["technical_gates_passed"])
            self.assertEqual(result["decision"]["decision"], "ELIGIBLE_FOR_HUMAN_REVIEW")
            self.assertEqual(Path(result["package_dir"]), older)
            self.assertFalse((newer / "state2_review.json").exists())
            self.assertTrue((older / "state2_review.json").exists())

    def test_latest_promotion_skips_newer_held_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            newer = create_lifecycle_package(
                root,
                "newer-held",
                review_approved=False,
                review_timestamp="2026-07-17T12:00:00Z",
            )
            older = create_lifecycle_package(
                root,
                "older-eligible",
                review_approved=True,
                review_timestamp="2026-07-17T11:00:00Z",
            )
            evaluator = State2PromotionEvaluator(
                package_dir=None,
                latest_root=root,
                min_candidates=4,
                min_review_ready_ratio=1.0,
                require_approved_review=True,
                max_routing_mismatches=0,
                max_missing_content=0,
                dry_run=False,
                notes=None,
            )

            result = evaluator.run()

            self.assertTrue(result["decision"]["approved"])
            self.assertEqual(Path(result["package_dir"]), older)
            self.assertFalse((newer / "state2_promotion_decision.json").exists())
            self.assertTrue((older / "state2_promotion_decision.json").exists())

    def test_latest_handoff_skips_newer_held_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            newer = create_lifecycle_package(
                root,
                "newer-held",
                review_approved=True,
                review_timestamp="2026-07-17T10:00:00Z",
                promotion_approved=False,
                promotion_timestamp="2026-07-17T12:00:00Z",
            )
            older = create_lifecycle_package(
                root,
                "older-eligible",
                review_approved=True,
                review_timestamp="2026-07-17T09:00:00Z",
                promotion_approved=True,
                promotion_timestamp="2026-07-17T11:00:00Z",
            )
            builder = State1HandoffBuilder(
                package_dir=None,
                latest_root=root,
                min_candidates=4,
                require_approved_review=True,
                require_approved_promotion=True,
                max_routing_mismatches=0,
                max_missing_content=0,
                dry_run=False,
                notes=None,
            )

            result = builder.run()

            self.assertTrue(result["decision"]["approved"])
            self.assertEqual(Path(result["package_dir"]), older)
            self.assertFalse((newer / "state1_handoff.json").exists())
            self.assertFalse((newer / "freeze_ready_manifest.json").exists())
            self.assertTrue((older / "state1_handoff.json").exists())
            self.assertTrue((older / "freeze_ready_manifest.json").exists())

    def test_held_handoff_does_not_emit_freeze_ready_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / "held-handoff"
            write_json(package_dir / "manifest.json", {"dataset_version": "held-handoff"})
            write_jsonl(package_dir / "dataset.jsonl", [candidate("candidate-1")])
            write_json(
                package_dir / "state2_review.json",
                {
                    "decision": {"approved": True, "decision": "ELIGIBLE_FOR_HUMAN_REVIEW"},
                    "review_metrics": {
                        "review_ready_ratio": 1.0,
                        "routing_mismatch_count": 0,
                        "missing_content_count": 0,
                    },
                    "exceptions": {},
                },
            )
            write_json(
                package_dir / "state2_promotion_decision.json",
                {
                    "decision": {"approved": False, "decision": "HOLD_STATE2_PACKAGE"},
                    "promotion_metrics": {"review_ready_ratio": 1.0},
                },
            )
            builder = State1HandoffBuilder(
                package_dir=package_dir,
                latest_root=None,
                min_candidates=1,
                require_approved_review=True,
                require_approved_promotion=True,
                max_routing_mismatches=0,
                max_missing_content=0,
                dry_run=False,
                notes=None,
            )

            result = builder.run()

            self.assertFalse(result["decision"]["approved"])
            self.assertTrue((package_dir / "state1_handoff.json").exists())
            self.assertFalse((package_dir / "freeze_ready_manifest.json").exists())
            self.assertFalse(result["freeze_ready_manifest_written"])

    def test_held_freeze_writes_no_freeze_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / "held-freeze"
            write_json(package_dir / "manifest.json", {"dataset_version": "held-freeze"})
            write_jsonl(package_dir / "dataset.jsonl", [candidate("candidate-1")])
            write_json(
                package_dir / "state2_review.json",
                {"decision": {"approved": True}, "review_metrics": {}, "exceptions": {}},
            )
            write_json(
                package_dir / "state2_promotion_decision.json",
                {"decision": {"approved": False}},
            )
            write_json(
                package_dir / "state1_handoff.json",
                {"decision": {"approved": False}, "handoff_metrics": {}},
            )
            write_json(
                package_dir / "freeze_ready_manifest.json",
                {"freeze_posture": {"freeze_ready": False}},
            )
            freezer = State1Freezer(
                package_dir=package_dir,
                latest_root=None,
                min_candidates=1,
                require_approved_review=True,
                require_approved_promotion=True,
                require_approved_handoff=True,
                require_freeze_ready=True,
                max_routing_mismatches=0,
                max_missing_content=0,
                dry_run=False,
                notes=None,
            )

            result = freezer.run()

            self.assertFalse(result["decision"]["approved"])
            self.assertFalse(result["written"])
            self.assertFalse(result["freeze_outputs_written"])
            self.assertFalse((package_dir / "freeze").exists())

    def test_held_registry_update_does_not_modify_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package_dir = root / "held-registry"
            freeze_dir = package_dir / "freeze"
            for filename in (
                "manifest.json",
                "state2_review.json",
                "state2_promotion_decision.json",
                "state1_handoff.json",
                "freeze_ready_manifest.json",
            ):
                write_json(package_dir / filename, {})
            write_json(
                freeze_dir / "state1_freeze.json",
                {
                    "decision": {"approved": False, "decision": "HOLD_STATE1_PACKAGE"},
                    "freeze_ready_summary": {"freeze_ready": False},
                },
            )
            write_json(
                freeze_dir / "frozen_manifest.json",
                {"dataset_version": "held-registry", "state": "STATE_1"},
            )
            write_jsonl(freeze_dir / "frozen_dataset.jsonl", [candidate("candidate-1")])
            registry_path = root / "state1_dataset_registry.json"
            original_registry = {
                "registry_id": "registry-1",
                "created_at": "2026-07-17T00:00:00Z",
                "updated_at": "2026-07-17T00:00:00Z",
                "entries": [],
            }
            write_json(registry_path, original_registry)
            original_bytes = registry_path.read_bytes()
            updater = State1RegistryUpdater(
                package_dir=package_dir,
                latest_root=None,
                registry_path=registry_path,
                require_approved_freeze=True,
                require_state1=True,
                dry_run=False,
                notes=None,
            )

            result = updater.run()

            self.assertFalse(result["decision"]["approved"])
            self.assertFalse(result["registry_modified"])
            self.assertEqual(registry_path.read_bytes(), original_bytes)
            self.assertFalse((freeze_dir / "state1_registry_update.json").exists())


if __name__ == "__main__":
    unittest.main()
