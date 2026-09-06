# Q-Pathformer Enterprise v2 Developer Assistance Protocol

**Document ID:** `QPATH-V2-DA-001`
**Version:** `1.0-draft`
**Status:** Execution companion pending M00 approval
**Owner:** Q-Pathformer Release Owner
**Authority:** Working-method guidance only
**Master specification:** [QPATHFORMER_V2_MASTER_DEVELOPMENT_SPEC.md](planning/QPATHFORMER_V2_MASTER_DEVELOPMENT_SPEC.md)

## 1. Purpose

This document defines how a developer, reviewer, coding assistant, or document
assistant shall support the Q-Pathformer Enterprise v2 workstream. It turns the
master specification into a safe session-by-session working method.

This protocol does not grant authority to stage, commit, tag, configure a
remote, push, upload assets, publish, approve a gate, issue a CSC result, or
make governance decisions. Human approval remains controlling.

## 2. Sources of Truth

Before work begins, read the records relevant to the active phase:

1. [Master development specification](planning/QPATHFORMER_V2_MASTER_DEVELOPMENT_SPEC.md)
2. [Public release export plan](planning/migration/V2_PUBLIC_RELEASE_EXPORT_DEV_PLAN.md)
3. [CSC evidence and refinement plan](planning/optimization/QPATHFORMER_V2_CSC_EVIDENCE_AND_REFINEMENT.md)
4. [Pre-TR-010 stabilization audit](planning/migration/PRE_TR010_STABILIZATION_AUDIT_20260717.md)
5. [Baseline staging allowlist](planning/migration/V2_BASELINE_STAGING_ALLOWLIST.md)
6. [TR-010 paper source brief](planning/optimization/QPATHFORMER_V2_TR010_PAPER_SOURCE_BRIEF.md)

Verified code, schemas, tests, and cryptographic behavior take precedence over
narrative text. A discrepancy shall be recorded and escalated; it shall not be
resolved by silently changing a claim or weakening a control.

## 3. Human and Assistant Roles

| Role | May do | Shall not do without separate authority |
|---|---|---|
| Human release owner | Select scope, mode, and proposed release treatment. | Bypass failed controls or misstate evidence. |
| Human reviewer | Approve, reject, or hold a recorded gate. | Approve an unverified or unidentified candidate. |
| Release engineer | Execute the exact approved phase and produce evidence. | Expand scope or infer publication authority. |
| Development assistant | Inspect, draft, patch, test, summarize, and identify risks within approved scope. | Stage, commit, tag, push, publish, create remotes, upload assets, generate private keys, or approve a gate by inference. |
| Automated checker | Produce repeatable observations and test results. | Act as governance authority or human approval. |

AI-assisted output is advisory and operational support. It does not constitute
independent assurance, certification, governance authority, release approval,
or evidence that a human reviewed the result.

## 4. Standard Working Cycle

Every task shall follow this order:

1. **Orient:** Confirm repository, branch, current HEAD, worktree state, active
   phase, selected mode, and governing-document versions.
2. **Inspect:** Read the relevant implementation, records, and existing user
   changes before proposing edits.
3. **Bound:** State files to be read, files to be written, checks to run, and
   actions that remain prohibited.
4. **Implement:** Make the smallest change that satisfies the active phase.
5. **Verify:** Run applicable tests, schema checks, documentation checks, and
   repository-state checks.
6. **Record:** Produce a dated result with status, evidence, exceptions, and
   next authorized action.
7. **Pause:** Stop at the phase gate. Do not begin the next phase without its
   recorded prerequisite or required human approval.

## 5. Session Start Checklist

Record the following before any write operation:

- Repository path and intended workspace.
- Current branch and HEAD.
- Current Git status, including untracked files.
- Active master-specification version and digest if M00 has passed.
- Active phase and last passed gate.
- Selected mode: `Mode A` or `Mode B`.
- Human owner and approver named by M00.
- Public target state: absent, empty, disposable rehearsal, frozen candidate,
  or committed public tree.
- Exact files authorized for modification.
- Whether source freeze at M05 has occurred.
- Whether target freeze at M11 has occurred.

If the active phase, authority, target identity, or freeze state is unclear,
the task status is `HOLD` and only read-only inspection may continue.

## 6. Repository Safety Rules

- Preserve unrelated user changes in a dirty worktree.
- Never use broad staging such as `git add -A` or `git add .`.
- Never use destructive reset, checkout, clean, or recursive delete to solve a
  release-preparation issue.
- Use explicit paths for copying, staging, hashing, and review.
- Reject symlinks, junctions, reparse points, path traversal, and destination
  escape during export.
- Never place a private key, credential, token, local environment file, or
  machine secret in the source or target repository.
- Do not write to the public target before M07.
- Do not change the source after M05.
- Do not change target regular files after M11.
- Git metadata created after M11 shall not alter frozen regular-file bytes.
- Do not treat an existing file as approved merely because it is tracked.
- Do not treat an untracked file as safe merely because `git diff --check`
  reports no issue.

Unexpected concurrent changes that affect active files require `HOLD` and
human direction. Unrelated changes shall be left untouched.

## 7. Phase Assistance Map

| Phase | Assistant focus | Required stop point |
|---|---|---|
| M00 | Prepare role, mode, authority, and governing-document records. | Stop for human approval. |
| M01 | Technical TR-010 draft, controlled placeholders, and source allowlist. | Stop when claims and allowlist are review-ready. |
| M02 | Read-only dependency, licence, provenance, model, registry, and document audit. | Do not create the public target. |
| M03 | Prepare Path 3 reconciliation and decision records. | Do not decide legal or release treatment by inference. |
| M04 | Implement and test fail-closed export tooling. | Do not freeze source until tests pass. |
| M05 | Verify the selected baseline and prepare explicit Git actions. | Commit and tag require exact approval. |
| M06 | Run exporter against a disposable target and compare outputs. | Mode B stops here. |
| M07 | Create and populate the controlled target from the M05 anchor. | Stop if target is non-empty or differs from allowlist. |
| M08 | Package qualified, Path 2-sourced historical v1 CSC evidence. | Do not regenerate or relabel v1 artifacts. |
| M09 | Complete portable docs, notices, dependency lock, disclosure, and CI. | Stop if licence or model provenance is unresolved. |
| M10 | Execute full source and target verification. | Any unexplained warning is `HOLD`. |
| M11 | Freeze regular files and generate final inventory, report, and checksums. | No further target regular-file writes. |
| M12 | Support external human review against frozen digests. | Review record remains outside target. |
| M13A | Prepare exact local public-commit operation and verify Git tree. | Requires explicit commit authorization. |
| M13B | Prepare exact tag, remote, push, and asset operation. | Requires second explicit publication authorization. |
| M13C | Prepare external attestation and final TR-010 binding. | Do not modify frozen repository. |
| M14 | Implement the versioned CSC Assurance Record in new slices. | Do not alter historical v1a contracts. |

## 8. Gate Result Format

Every gate record shall contain:

```text
document_id:
phase:
mode:
result: PASS | FAIL | HOLD | NOT_APPLICABLE
repository:
branch:
source_head:
source_baseline_commit:
target_path:
target_state:
started_at_utc:
completed_at_utc:
executor:
reviewer:
reviewer_authority:
inputs:
outputs:
commands_or_methods:
checks:
exceptions:
evidence_references:
next_authorized_phase:
approval_reference:
```

Use `PASS` only when every mandatory check for the phase has passed. Use
`NOT_APPLICABLE` only with a reason and approving authority. A warning that can
affect integrity, licensing, provenance, evidence identity, or claim accuracy
is `HOLD`, not `PASS`.

## 9. Evidence and Provenance Rules

### 9.1 Git Identities

Keep these identities separate in every summary:

- Historical v1 tag and commit.
- Local v2 source-baseline commit.
- Public v2 release commit and tag.
- Publication inventory and checksum digests.

Never substitute one identity for another or call the dirty v2 worktree an
immutable baseline.

### 9.2 Historical Evidence Classes

Use only these classes:

- `UPSTREAM_ACCESS_POD_V1A`
- `V1_ENTERPRISE_CSC_BRIDGE`
- `HISTORICAL_V1_CSC_EVIDENCE`
- `V1_EXAMPLE_ARTIFACT`
- `V1_RESEARCH_OR_SUPERSEDED`

Preserve upstream, enterprise bridge, generated evidence, examples, and
research outputs as separate concepts.

### 9.3 CSC Rules

- The controlling active v1 source set is
  `shared/standards/access_pod/STANDARDS_PAPER_SOURCE_SET_20260415.md`.
- Originating CSC session evidence comes from Path 2.
- Path 1 and Path 3 may provide context but are not CSC session sources.
- Finance and healthcare are mapper-driven baselines.
- Public and AI/emerging-tech are curated examples.
- Coverage, provisionality, confidence, and sector-validation qualifications
  shall accompany every historical level.
- Historical artifacts shall not be recalculated, re-signed, or relabelled as
  v2 results.
- `CSC Assurance Record` is the non-certifying v2 working term.

### 9.4 Historical Bytes

Do not normalize vendored or historical bytes merely to remove absolute paths
or formatting defects. Record inert historical metadata as a limitation and
verify preserved bytes against applicable manifests.

## 10. Documentation and Claim Rules

- Use `public source release` or `source-available public-review release` under
  the current Q-Pathformer platform licence.
- Preserve nested MIT notices for Access-PoD material.
- Do not call the repository a base-model distribution.
- Do not imply model redistribution rights from the platform licence.
- Do not cite unchecked historical checklists as completed verification.
- Do not document directories absent from the selected public tree.
- Generate repository layout from the target rather than manually maintaining
  a full tree.
- Validate Markdown headings, rendering, links, and file references.
- State clearly when a result proves execution continuity but not model quality
  or governance effectiveness.
- Record AI assistance and human authority accurately.

## 11. TR-010 Assistance Rule

The repository-facing document is
`docs/release/TR010_RELEASE_BOUNDARY.md`. The final APOD-TR-010 paper is
external to the frozen repository and is finalized only after the public
commit and tag exist.

Before M13C, commit, tag, inventory, evidence-pack, and asset identifiers in
the technical draft remain controlled placeholders. An assistant shall not
invent an identifier or create a self-referential repository paper.

## 12. Freeze and Publication Discipline

After M11:

- No target regular file may change.
- The human review record is external.
- The public commit SHA is recorded externally.
- The release-asset manifest and post-publication attestation are external.
- Any required content correction invalidates the freeze and returns the work
  to the appropriate earlier phase for a new candidate build.

Commit, tag, remote, push, release creation, asset upload, and publication are
separate actions. Approval for one does not authorize another.

## 13. Assistant Handoff Template

Use this structure when ending a work session:

```text
Active phase:
Result: PASS | FAIL | HOLD | NOT_APPLICABLE
Completed scope:
Files changed:
Files generated:
Checks run and outcomes:
Repository branch and HEAD:
Source freeze state:
Target path and state:
Known findings:
Unresolved decisions:
Actions not performed:
Next permitted action:
Required human approval:
```

The handoff shall distinguish observed facts, inferences, proposals, and human
decisions. It shall never report a release as approved merely because tooling
completed successfully.

## 14. Current Working Position

The master document is ready for M00 review. Public export remains
unauthorized. M02 is the next permitted technical activity only after M00 and
M01 have named roles, selected a mode, recorded approval, prepared the
technical TR-010 draft posture, and approved the source allowlist.

Current status:

`MASTER_SPEC_READY`

Current public export authorization:

`NOT_AUTHORIZED`
