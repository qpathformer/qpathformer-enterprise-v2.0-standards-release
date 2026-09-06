# Q-Pathformer Enterprise v2 Release Process for APOD-TR-010

**Document ID:** `QPATH-V2-TR010-RELEASE-SOURCE-001`  
**Version:** `1.0-draft`  
**Date:** `2026-07-18`  
**Status:** `TR010_DRAFTING_SOURCE_NOT_RELEASE_ARTIFACT`  
**Scope:** M00 through corrected M11, with M12 and later gates explicitly bounded  
**Companion:** `QPATHFORMER_V2_TR010_RESULTS_AND_V1_COMPARISON.md`

## 1. Purpose

This record provides the release-engineering narrative and command surface for
drafting APOD-TR-010. It explains how Q-Pathformer Enterprise v2 was selected,
verified, exported, qualified, and frozen as a public-review release candidate.

This document is external to the frozen candidate. It does not modify the
candidate, authorize M12 approval, create a public Git identity, or authorize a
ZIP, push, release asset, or publication.

## 2. Current Release Position

The current controlled state is:

| Item | Current value |
| --- | --- |
| Historical v1.0 tag | `v1.0-qpathformer-enterprise` |
| Historical v1.0 commit | `0fa94ecf47d698a894bc868545f110570d0dec50` |
| V2 source-baseline commit | `cf9721afb81273d82667dd7b33ee5e5f3ad806d9` |
| V2 source-baseline tag | `v2.0-qpathformer-enterprise-source-baseline` |
| V2 source Git tree | `866cb4246d4fdc5e31c3a8be32249dc1b00b60ec` |
| Controlled candidate | `C:\qpathformer_enterprise_v2_release` |
| Corrected M11 result | `PASS` |
| Candidate state | `READY_FOR_M12_RECONSIDERATION` |
| Public commit and tag | Not created |
| ZIP and release asset | Not created |
| Push and publication | Not performed |
| APOD-TR-010 final binding | Not yet performed |

The first M12 technical review held the earlier M11 candidate for three
release-surface findings. The Human Release Authority authorized only those
three corrections and the required M10 and M11 rebuild. The corrected M11
candidate now awaits a new, separately authorized M12 human disposition.

The frozen candidate uses Platform License 1.0 with the corrected custom SPDX
identifier `LicenseRef-QPATHFORMER-PLATFORM-1.0`. Platform Licence 1.1 remains
an external, non-operative legal-review draft and is not part of this candidate.

## 3. Release Principles

The release process applied the following constraints:

- Human authority controlled every gated transition.
- The v2 source baseline was committed and tagged before public export.
- Export used an exact allowlist and failed closed on path or hash mismatch.
- Historical bytes were preserved unless an approved active-text normalization
  rule applied.
- Model weights, adapters, checkpoints, mutable registries, private keys,
  caches, and local environment files were excluded.
- Historical v1.0 results were retained as evidence rather than regenerated or
  relabelled as v2 results.
- The defective historical Path 3 freeze bundle was excluded from positive v2
  evidence.
- A lifecycle state, package seal, score, or successful test did not create
  training, deployment, certification, or publication authority.
- The final APOD-TR-010 paper remains external so it can bind final public
  identifiers without self-reference.

## 4. End-to-End Gate Record

| Gate | Work performed | Result and evidence |
| --- | --- | --- |
| M00 | Defined Mode A scope, roles, authority, stop conditions, and external-paper policy. | `PASS`; `planning/MASTER_SCOPE_RECORD.md`. |
| M01 | Prepared the TR-010 skeleton, source brief, claim boundaries, and controlled placeholders. | `PASS`; no future identifier was invented. |
| M02 | Mapped dependencies, public files, large assets, duplicate documents, third parties, model provenance, registries, paths, and transformations. | Complete and accepted into M03. |
| M03 | Resolved publication form, model exclusion, Path 3 provenance, historical CSC selection, registry treatment, licences, and duplicate roles. | `PASS`; Path 3 `QPDS-PACKAGE-001` excluded from positive evidence. |
| M04 | Implemented and tested the allowlist exporter, deterministic text policy, path controls, and external logging. | `PASS`; 320-file dry run, deterministic tree digest. |
| M05 | Staged only 68 approved source-baseline paths, verified the source, and created the authorized local commit and annotated tag. | `PASS`; commit `cf9721...`, tag `v2.0-qpathformer-enterprise-source-baseline`. |
| M06 | Exported two disposable candidates and verified both independently. | `PASS`; both produced 320 files, 35,414,938 bytes, and digest `62a866...`. |
| M07 | Created the previously absent controlled target in one allowlisted export pass. | `PASS`; exact match to M06 and no target Git metadata. |
| M08 | Retrieved and qualified the selected historical v1.0 CSC source set from the immutable v1 tag. | `PASS`; 25 selected artifacts across four profiles, all Path 2-sourced. |
| M09 | Added release documentation, notices, dependency locks, layout, validation, and CI. | Initial `HOLD` for vendor-manifest mismatch; superseded by transparent canonical-equivalence `PASS`. |
| M09 resolution | Retained all six physical files, recorded physical and canonical identities, and defined a non-retroactive v2 scoring design baseline. | `PASS`; 3 byte-exact and 6 CRLF-to-LF canonical-equivalent entries. |
| M10 | Reconciled source, target, overlays, historical evidence, schemas, CLIs, dependencies, tests, and exclusions. | `PASS`; later rerun after bounded M12 remediation also passed. |
| M11 | Generated the publication inventory, build report, and checksums in non-circular order, then performed read-only verification. | Corrected rebuild `PASS`; 351 files and final digest `9682ef...`. |
| M12 | Independently reviewed the first frozen candidate. | Initial `HOLD`; SPDX, remote installer, and movable CI action findings identified. |
| M12 remediation loop | Returned only to M09 for M12-F01 through M12-F03, then reran M10 and rebuilt M11. | All three findings resolved; new M12 reconsideration is not yet authorized. |
| M13A | Create and verify the local public commit. | Not authorized or performed. |
| M13B | Create the public tag, remote, push, ZIP, checksums, and release assets. | Not authorized or performed. |
| M13C | Publish the external attestation and bind final APOD-TR-010. | Not authorized or performed. |
| M14 | Begin the separately versioned CSC Assurance Record implementation. | Future work; current scoring contract is a non-enforced design baseline. |

## 5. Command Conventions

The commands below are PowerShell 7 templates reconstructed from the validated
CLI interfaces and gate records. Commands that create commits, tags, targets,
inventories, or checksums are marked as gated and shall not be rerun against
the controlled candidate without a new authorization.

```powershell
$SourceRoot = 'C:\qpathformer_enterprise_v2'
$TargetRoot = 'C:\qpathformer_enterprise_v2_release'
$RecordsRoot = 'C:\qpathformer_enterprise_v2_release_records'
$Allowlist = Join-Path $SourceRoot 'planning\migration\V2_PUBLIC_COPY_ALLOWLIST.json'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

## 6. M02-M04 Preflight and Exporter Verification

Run source checks without creating the public target:

```powershell
Set-Location $SourceRoot

git status --short
git diff --check

py -3 -B -m unittest discover `
  -s .\tests\unit `
  -p 'test_*.py' `
  -v

py -3 -B .\scripts\export_v2_public_release.py `
  --source-root $SourceRoot `
  --target-root 'C:\qpathformer_v2_export_dry_run' `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M04\export_dry_run.json') `
  --dry-run
```

Expected M04 dry-run identity:

| Field | Expected value |
| --- | ---: |
| Resolved files | 320 |
| Source bytes | 35,442,108 |
| Expected target bytes | 35,414,938 |
| Expected target digest | `62a866976506a65b9e238faa5e9e94d6f32c8991f1b2795a4561fdd3e6ed3080` |

## 7. M05 Source Baseline Commands

The following sequence records the historical gated method. The exact 68 paths
were expanded from `V2_BASELINE_STAGING_ALLOWLIST.md`; whole-tree staging was
prohibited.

```powershell
Set-Location $SourceRoot

git status --short
git diff --cached --name-status
git diff --cached --check

# GATED: expand only the exact paths listed in the approved baseline allowlist.
$ApprovedBaselinePaths = @(
  # Insert the 68 reviewed repository-relative paths here.
)
if ($ApprovedBaselinePaths.Count -ne 68) {
  throw 'The approved M05 baseline must contain exactly 68 staged paths.'
}
git add -- $ApprovedBaselinePaths

git diff --cached --name-status
git diff --cached --check

# GATED: these identifiers were separately authorized for M05.
git commit -m 'release: establish Q-Pathformer Enterprise v2 source baseline'
git tag -a 'v2.0-qpathformer-enterprise-source-baseline' `
  -m 'Q-Pathformer Enterprise v2 source baseline'

git rev-parse 'refs/tags/v2.0-qpathformer-enterprise-source-baseline^{commit}'
git rev-parse 'refs/tags/v2.0-qpathformer-enterprise-source-baseline^{tree}'
git status --short
```

The resolved commit and tree shall equal the identifiers in Section 2.

## 8. M06 Deterministic Export Rehearsal

Each target shall be absent or empty before export:

```powershell
$CandidateA = 'C:\qpathformer_v2_rehearsal_a'
$CandidateB = 'C:\qpathformer_v2_rehearsal_b'

py -3 -B (Join-Path $SourceRoot 'scripts\export_v2_public_release.py') `
  --source-root $SourceRoot `
  --target-root $CandidateA `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M06\candidate_a_export.json')

py -3 -B (Join-Path $SourceRoot 'scripts\export_v2_public_release.py') `
  --source-root $SourceRoot `
  --target-root $CandidateA `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M06\candidate_a_verify.json') `
  --verify-only

py -3 -B (Join-Path $SourceRoot 'scripts\export_v2_public_release.py') `
  --source-root $SourceRoot `
  --target-root $CandidateB `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M06\candidate_b_export.json')

py -3 -B (Join-Path $SourceRoot 'scripts\export_v2_public_release.py') `
  --source-root $SourceRoot `
  --target-root $CandidateB `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M06\candidate_b_verify.json') `
  --verify-only
```

M06 passed only after both targets had identical file sets and digests and the
source worktree remained unchanged.

## 9. M07 Controlled Target Export

This was a separately authorized one-time target-creation action:

```powershell
# GATED: $TargetRoot must be absent or empty before this command.
py -3 -B (Join-Path $SourceRoot 'scripts\export_v2_public_release.py') `
  --source-root $SourceRoot `
  --target-root $TargetRoot `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M07\controlled_target_export.json')

py -3 -B (Join-Path $SourceRoot 'scripts\export_v2_public_release.py') `
  --source-root $SourceRoot `
  --target-root $TargetRoot `
  --allowlist $Allowlist `
  --log-output (Join-Path $RecordsRoot 'M07\controlled_target_verify.json') `
  --verify-only
```

The target was not initialized as a Git repository.

## 10. M08 Historical CSC Qualification

The selected source was retrieved from the immutable v1.0 tag rather than a
moving branch. The exact 26-path source set is bound by the M08 evidence
manifest. The controlled method was equivalent to:

```powershell
Set-Location $SourceRoot

git rev-parse 'v1.0-qpathformer-enterprise^{commit}'
git rev-parse 'v1.0-qpathformer-enterprise^{tree}'

# GATED TEMPLATE: expand the 26 approved paths from the M08 source set.
$ApprovedM08SourcePaths = @(
  # Insert the 26 reviewed repository-relative paths here.
)
if ($ApprovedM08SourcePaths.Count -ne 26) {
  throw 'The approved M08 source set must contain exactly 26 paths.'
}
git archive --format=zip `
  --output (Join-Path $RecordsRoot 'M08\v1_csc_source_set.zip') `
  v1.0-qpathformer-enterprise `
  -- $ApprovedM08SourcePaths

Get-FileHash -Algorithm SHA256 `
  -LiteralPath (Join-Path $RecordsRoot 'M08\v1_csc_source_set.zip')
```

The selected artifacts were byte-compared with the tag and then described in
`release/V1_CSC_EVIDENCE_MANIFEST.json`. They were not regenerated under v2.

## 11. M09-M10 Release Validation

The pre-freeze candidate was validated without a model download or GPU. The
report-generating command writes release bytes and is therefore limited to an
authorized M09 or M10 run. Reviewers of the frozen M11 candidate shall use only
the read-only `--check-only` form.

```powershell
Set-Location $TargetRoot

py -3 -m pip install -r .\requirements-release.txt

# GATED PRE-FREEZE WRITE: do not run this against the frozen M11 candidate.
py -3 -B .\scripts\validate_v2_release.py `
  --root . `
  --report-output release/DOCUMENTATION_CONFORMANCE_REPORT.json

# READ-ONLY RELEASE REVIEW.
py -3 -B .\scripts\validate_v2_release.py `
  --root . `
  --check-only

py -3 -B -m unittest discover `
  -s .\tests\unit `
  -p 'test_*.py' `
  -v

$env:PYTHONPYCACHEPREFIX = Join-Path $env:TEMP 'qpathformer-v2-pycache'
py -3 -m compileall -q .\scripts .\tests\unit
py -3 -m pip check
```

The corrected M10 evidence recorded 23 of 23 release checks, 27 valid schemas,
19 resolved reviewer CLIs, 24 unit tests with one environment-guarded skip,
and no unexplained warning.

## 12. M11 Ordered Freeze Commands

The M11 builder is a controlled release-engineering helper outside the public
candidate. The mandated order prevented circular identity claims:

```powershell
$M11Builder = '<CONTROLLED_RELEASE_ENGINEERING_ROOT>\build_m11_release.py'
$Inventory = Join-Path $TargetRoot 'release\PUBLICATION_INVENTORY.json'
$BuildReport = Join-Path $TargetRoot 'release\RELEASE_CANDIDATE_BUILD_REPORT.md'
$Checksums = Join-Path $TargetRoot 'release\SHA256SUMS.txt'

# GATED: run only after an authorized, clean M10 PASS state.
py -3 -B $M11Builder inventory `
  --root $TargetRoot `
  --output $Inventory

py -3 -B $M11Builder build-report `
  --root $TargetRoot `
  --output $BuildReport `
  --m10-report-sha256 e1681d941e1ce03eef2def0038286a07caa8d49e2a7863ab2fe940b9ba48a218 `
  --m10-gate-sha256 4252fa6ee78f8aaa295e29afb61304567d07b3eca631a17d89682b0de5877741

py -3 -B $M11Builder checksums `
  --root $TargetRoot `
  --output $Checksums

py -3 -B $M11Builder verify `
  --root $TargetRoot `
  --output (Join-Path $RecordsRoot 'M11\m11_rebuild_frozen_tree_verification.json')
```

The inventory excludes itself, the build report, and the checksum file. The
checksum file is written last and covers every final regular file except
itself.

## 13. M12 Human Review Boundary

M12 is not an automated approval command. The technical reviewer reproduces
the frozen identity, checks release claims and supply-chain controls, records
findings, and provides evidence to the designated human reviewer. The human
reviewer then records `PASS`, `FAIL`, or `HOLD` and the next authorized action.

A read-only technical identity check uses:

```powershell
py -3 -B $M11Builder verify `
  --root $TargetRoot `
  --output (Join-Path $RecordsRoot 'M12\m12_read_only_verification.json')
```

The current corrected candidate passed this read-only identity check, but no
new M12 human approval has been recorded.

## 14. V2 Training Authorization and Package-Seal Reproduction

These commands exercise the implemented v2 control boundary. They do not
authorize a production training run. Private keys shall remain outside the
repository and authorization and package-seal roles shall use different keys.

```powershell
Set-Location $TargetRoot
py -3 -m pip install -r .\requirements-crypto.txt

$V2KeyRoot = Join-Path $HOME '.qpathformer\v2_keys'
New-Item -ItemType Directory -Path $V2KeyRoot -Force | Out-Null

py -3 .\scripts\generate_ed25519_keypair_v2.py `
  --private-key (Join-Path $V2KeyRoot 'authorization.private.pem') `
  --public-key (Join-Path $V2KeyRoot 'authorization.public.pem') `
  --key-id 'authorization-review-key-v1' `
  --role authorization_signer

py -3 .\scripts\generate_ed25519_keypair_v2.py `
  --private-key (Join-Path $V2KeyRoot 'package-seal.private.pem') `
  --public-key (Join-Path $V2KeyRoot 'package-seal.public.pem') `
  --key-id 'package-seal-key-v1' `
  --role package_sealer

py -3 .\scripts\create_training_authorization_v2.py `
  --dataset-version $DatasetVersion `
  --dataset-path $SourceDatasetPath `
  --registry-entry-id $RegistryEntryId `
  --decision ALLOW `
  --scope validation_parameter_update `
  --reviewer-id 'reviewer-id' `
  --decision-source 'controlled_v2_review' `
  --rationale 'Authorized for one bounded local validation parameter-update run.' `
  --key-id 'authorization-review-key-v1' `
  --private-key (Join-Path $V2KeyRoot 'authorization.private.pem') `
  --valid-for-hours 168 `
  --acknowledge-human-decision `
  --output .\authorizations\training_authorization.json

py -3 .\scripts\run_training_state1.py `
  --dataset-version $DatasetVersion `
  --registry-path .\shared\registry\state1_dataset_registry.json `
  --authorization-file .\authorizations\training_authorization.json `
  --authorization-public-key (Join-Path $V2KeyRoot 'authorization.public.pem') `
  --authorization-scope validation_parameter_update `
  --package-seal-private-key (Join-Path $V2KeyRoot 'package-seal.private.pem') `
  --package-seal-key-id 'package-seal-key-v1' `
  --output-root .\path_2_access_mode_canonical\03_dataset\training_packages `
  --backend-profile .\shared\configs\training_backend_profile.local_lora.json

py -3 .\scripts\verify_training_package_seal_v2.py `
  --package-dir $V2TrainingPackage `
  --dataset-version $DatasetVersion `
  --registry-entry-id $RegistryEntryId `
  --public-key (Join-Path $V2KeyRoot 'package-seal.public.pem')

py -3 .\scripts\run_state1_finetune_local_lora.py `
  --training-package $V2TrainingPackage `
  --authorization-public-key (Join-Path $V2KeyRoot 'authorization.public.pem') `
  --package-seal-public-key (Join-Path $V2KeyRoot 'package-seal.public.pem') `
  --authorization-scope validation_parameter_update `
  --output-root .\path_1_tr_corpus_reference\05_runs `
  --run-label v2_authorized_sealed_validation `
  --dry-run
```

The dry run verifies authorization and package integrity before creating a run
directory. A failure leaves no run artifact.

## 15. Path Execution Documents

The release-validation commands above test the v2 control and packaging
surface. End-to-end data-path commands remain in these shipped records:

| Path | Command record | V2 interpretation |
| --- | --- | --- |
| Path 1 | `docs/execution/path_1_tr_corpus_reference_commands.md` | Historical populated evidence; a future fine-tune requires v2 authorization and sealing. |
| Path 2 source-first | `docs/execution/path_2_access_mode_canonical_source_first_commands.md` | Historical populated lifecycle evidence; v2 preparation requires explicit authorization. |
| Path 2 runtime | `docs/execution/path_2_access_mode_canonical_runtime_signal_commands.md` | Optional local-model signal route; model is not required for release validation. |
| Path 3 client JSON | `docs/execution/path_3_client_custom_dataset_commands.md` | Included populated positive example; remains contained in `STATE_3`. |
| Path 3 external bundle | `docs/execution/path_3_external_custom_adapter_commands.md` | Bring-your-own strict route; shipped defective v1 bundle is excluded from positive evidence. |
| CSC | `docs/execution/access_pod_csc_commands.md` | Historical v1 reproduction guidance; no v2 score was generated. |

## 16. Difference From the v1.0 Release Process

| Area | V1.0 release | V2 release candidate |
| --- | --- | --- |
| Release identity | Published historical tag and populated outputs. | Immutable source baseline plus deterministic allowlisted target, inventory, checksums, and external gate records. |
| Training permission | Lifecycle and legacy permission fields could be read as preparation signals. | Training requires explicit, scoped, time-limited, dataset-bound, registry-bound Ed25519 authorization. |
| Package integrity | Package artifacts and manifests existed without a separately signed complete member inventory. | Complete package inventory, deterministic Merkle root, and separate Ed25519 package-seal key are required. |
| Role separation | Human review existed, but cryptographic authorization and package-seal roles were not separated. | Authorization signer and package sealer use different keys and external trusted public keys. |
| Failure behavior | Some latest-package and held-output behavior could be ambiguous. | Tested review, promotion, handoff, freeze, registry, authorization, seal, and export boundaries fail closed. |
| Historical evidence | Path and CSC outputs were presented as active v1 release results. | The same results are preserved and explicitly labelled historical; v2 does not claim a new GPU or CSC run. |
| CSC interpretation | Numeric score objects remained primary despite sparse observation. | Historical scores remain non-retroactive; a separate observation-status and scoring design baseline is recorded but not yet enforced. |
| Public file selection | Broad release snapshot included model-derived and mutable artifacts. | Exact allowlist excludes model binaries, adapters, mutable registries, private keys, caches, and unreconciled positive evidence. |
| Path 3 bundle | Reported as hash-valid in the historical run record. | Immutable-tag audit found the bundle fails its own `hashes.txt`; it is retained only as a disclosed negative finding. |
| CI and dependencies | Reproducibility controls were less explicit. | Exact release dependency pins, immutable GitHub Action SHAs, release validator, and clean-tree CI are included. |
| Licence metadata | Custom identifier was not SPDX-compliant. | Corrected to `LicenseRef-QPATHFORMER-PLATFORM-1.0`; substantive 1.0 terms are unchanged. |
| Publication authority | Release actions were less formally decomposed. | Commit, tag, target, freeze, M12, ZIP, push, assets, and publication are separately gated human actions. |

## 17. Final TR-010 Binding Requirements

The final paper shall not be described as release-bound until later authorized
gates supply:

1. A new M12 human decision against the corrected M11 digest.
2. The public repository commit and tree.
3. The public release tag.
4. The release ZIP filename, size, and SHA-256, if a ZIP is authorized.
5. The post-upload verification and publication attestation.
6. The final APOD-TR-010 asset hash and publication locator.

Until then, this document is a complete drafting source and command record,
not a publication authorization.
