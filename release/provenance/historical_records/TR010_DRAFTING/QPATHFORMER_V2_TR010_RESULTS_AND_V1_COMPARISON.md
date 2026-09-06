# Q-Pathformer Enterprise v2 Results and v1.0 Comparison for APOD-TR-010

**Document ID:** `QPATH-V2-TR010-RESULTS-SOURCE-001`  
**Version:** `1.0-draft`  
**Date:** `2026-07-18`  
**Status:** `TR010_DRAFTING_SOURCE_NOT_RELEASE_ARTIFACT`  
**Evidence cutoff:** Corrected M11 freeze and subsequent read-only identity verification  
**Companion:** `QPATHFORMER_V2_TR010_RELEASE_PROCESS.md`

## 1. Results Boundary

This document separates three evidence classes:

1. Implemented and tested v2 controls.
2. V2 release-engineering and frozen-candidate results.
3. Historical v1.0 Path 1, Path 2, Path 3, model-run, and CSC evidence.

No historical model or CSC output was regenerated under v2. No new v2 GPU
fine-tune, model-quality comparison, production deployment, or CSC score is
claimed.

## 2. Current V2 Candidate Identity

| Identifier | Verified value |
| --- | --- |
| V2 source commit | `cf9721afb81273d82667dd7b33ee5e5f3ad806d9` |
| V2 source tag | `v2.0-qpathformer-enterprise-source-baseline` |
| V2 source Git tree | `866cb4246d4fdc5e31c3a8be32249dc1b00b60ec` |
| Publication inventory SHA-256 | `bed0957ddb1de0b3ed1b76c295f7febc12f7ca53880d7c1fd408996c2bcc07e6` |
| Listed pre-record files | 348 |
| Listed pre-record bytes | 35,619,880 |
| Canonical listed-file digest | `59ca99c9869cbd26d537a577b7d1f79f487cc999f39408e52c4fa07674f8915d` |
| Final checksum-set SHA-256 | `47a04a06dcc3595402c95f8028c0cf222ccc09351040b9a3fb76f399e87dbf75` |
| Checksum entries | 350 |
| Historical v1 CSC evidence-manifest SHA-256 | `e851bda7e77f459817055fc487cdaa38788cf13244c767d4222abd64c3085e0f` |
| Final regular files | 351 |
| Final bytes | 35,754,807 |
| Final canonical tree SHA-256 | `9682ef298961b5288d3c7a59134b6273511f1a066a705d221af71ce69d225bb0` |
| Current gate state | Corrected M11 `PASS`; awaiting separately authorized M12 reconsideration |

The candidate has no `.git` directory, public commit, public tag, ZIP, remote,
push, release asset, or publication record.

## 3. Gate Results

| Gate | Result | Measured outcome |
| --- | --- | --- |
| M00-M03 | `PASS` | Scope, authority, evidence classification, model treatment, Path 3 treatment, and public-file decisions established. |
| M04 | `PASS` | 320-file allowlist dry run; expected target digest `62a866...`. |
| M05 | `PASS` | Immutable source commit and annotated tag created from 68 explicitly staged baseline paths. |
| M06 | `PASS` | Two independent exports matched: 320 files, 35,414,938 bytes, zero mismatch. |
| M07 | `PASS` | Controlled target created once and matched M06 exactly. |
| M08 | `PASS` | 25 historical CSC artifacts selected from immutable v1 source; four Path 2 profiles qualified. |
| M09 | `HOLD`, then `PASS` | Vendor mismatch was resolved as transparent canonical equivalence without rewriting historical bytes. |
| M10 | `PASS` | Complete source-target reconciliation, conformance, tests, schemas, CLIs, dependencies, and exclusions passed. |
| First M11 | Superseded | Initial frozen digest `ef86494...` was held at M12 for three release-surface findings. |
| Bounded remediation | `PASS` | Corrected SPDX metadata, removed remote pipe-to-shell guidance, and pinned CI actions to full SHAs. |
| Corrected M10 | `PASS` | All authorized corrections and all release checks passed. |
| Corrected M11 | `PASS` | Final 351-file candidate frozen at digest `9682ef...`. |
| New M12 | Awaiting authorization | No corrected-candidate human disposition has been recorded. |

## 4. V2 Verification Results

### 4.1 Automated Tests

The final M10 suite ran 24 tests:

| Test area | Test count | Result |
| --- | ---: | --- |
| Ed25519 training authorization and migration | 4 | Passed |
| Allowlisted deterministic release export | 8 | 7 passed; 1 Windows symlink-capability test skipped by explicit environment guard |
| Fail-closed lifecycle behavior | 7 | Passed |
| Complete package inventory and Ed25519 sealing | 5 | Passed |
| Total | 24 | 23 passed; 1 skipped; 0 failed |

Direct operating-system reparse-point scanning passed, so the environment skip
did not leave an unexplained release finding.

### 4.2 Release Validation

| Check | Final result |
| --- | --- |
| Documentation and repository conformance | 23 of 23 passed |
| JSON Schemas | 27 valid; 0 invalid |
| Reviewer CLI entry points | 19 resolved; 0 failed |
| Source-target reconciliation | 11 of 11 passed |
| Exact release dependency pins | 8 |
| `pip check` | No broken requirements |
| Credentials or secrets | 0 findings |
| Private keys in candidate | 0 |
| Reparse points | 0 |
| Cache or bytecode files | 0 |
| Mutable registry records | 0 |
| Model or training binaries | 0 |
| Optimizer checkpoints or adapters | 0 |
| Unexplained warnings | 0 |

### 4.3 Export Determinism and Historical Preservation

| Measure | Result |
| --- | ---: |
| M06 independent targets | 2 |
| Files per M06 target | 320 |
| Bytes per M06 target | 35,414,938 |
| Cross-target file or hash mismatches | 0 |
| Byte-preserved historical files | 174 |
| Historical byte-preservation failures | 0 |
| Active text files normalized under policy | 146 |
| Extra or missing files | 0 |
| Source mutation detected | No |

### 4.4 Fail-Closed Behavior Demonstrated

The tests and retained examples substantiate the following behavior:

- Missing maturity evidence is treated as insufficient evidence.
- Latest-package selection skips newer held packages rather than silently
  treating them as eligible.
- A held handoff emits no freeze-ready manifest.
- A held freeze emits no frozen outputs.
- A held registry update does not mutate the registry.
- Legacy `fine_tuning_allowed` values do not create v2 authorization scope.
- Missing, expired, wrong-scope, wrong-dataset, wrong-registry, tampered, or
  wrong-key authorization fails before run output creation.
- Changed, added, or removed package files fail exact inventory verification.
- Altered package-seal metadata or the wrong package-seal key fails Ed25519
  verification.
- Authorization and package sealing require different key fingerprints.
- A failed package check leaves no fine-tune run directory.

These are implementation and test results. They do not establish independent
security assurance, production readiness, or legal authority.

## 5. Historical v1.0 Path Results

The following values are retained from the validated v1.0 run records.

| Path or option | Historical v1.0 result | V2 treatment |
| --- | --- | --- |
| Path 1 TR corpus | `checkpoint_v4_strict`; 16 documents; 846 signals; 1,241 source-signal rows; 1,117 train rows; 124 validation rows; package `QPDS-TR-STRICT-ID3-001`. | Preserved for inspection; future training requires v2 authorization and sealing. |
| Path 1 local LoRA | TinyLlama 1.1B completed on CUDA; aggregate training loss about `3.4113`; final logged loss about `3.4135`. | Historical execution continuity only; not model-quality proof. |
| Path 2 source-first | Four grouped scenarios and four candidates crossed the v1.0 gate through review, promotion, handoff, freeze, registry, and training-package preparation. | Preserved as strongest historical lifecycle trace; v2 adds explicit authorization. |
| Path 2 local LoRA | Four-record TinyLlama 1.1B run completed on CUDA; aggregate training loss about `3.7577`; final logged loss about `3.2855`. | Historical execution continuity only; 100 epochs over four records is not generalization evidence. |
| Path 2 runtime | Local `gpt-oss:20b` emitted a valid Path 2 runtime signal and one-candidate review package; promotion held below `min_candidates = 4`. | Preserved as a correct hold example; runtime model is optional and excluded from release validation. |
| Path 3 client JSON | One source file normalized to four records with hash status `ok`; remained in `STATE_3`. | Included as the populated positive v2 Path 3 example. |
| Path 3 freeze bundle | Historical run record reported six normalized records and hash status `ok`. | V2 audit found the immutable tagged files fail their own `hashes.txt`; excluded from positive evidence and retained only as a disclosed negative finding. |

The v1.0 path results shall not be combined with v2 control test results to
claim a v2 training outcome or a model-quality improvement.

## 6. Historical v1.0 CSC Results

M08 selected 25 artifacts from the immutable v1.0 source and bound them to
Path 2 run `RTRUN-llm-runtime-registration-check-20260413T095208Z-77a538bc`.
Path 1 and Path 3 are contextual only and did not originate these CSC records.

| Profile | Role | Composite | Level | Observed metrics | Coverage | Required qualification |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Finance | Mapper-driven v1 baseline | 91.9 | 5 | 16 of 60 | 26.67% | Provisional historical Level 5; governance-chain saturation and confidence remain explicit. |
| Healthcare | Mapper-driven v1 baseline | 84.6 | 4 | 12 of 60 | 20.00% | Narrow historical Level 4 with sparse observation; not a general healthcare claim. |
| Public | Curated v1 standards example | 93.0 | 5 | 12 of 60 | 20.00% | Not mapper-driven; retained as a standards example. |
| AI and emerging technology | Curated v1 standards example | 82.9 | 4 | 12 of 60 | 20.00% | Sector validation was not met; not a validated sector baseline. |

The v2 candidate does not recalculate these scores. It requires coverage,
confidence, direct-versus-proxy evidence, provisionality, and sector-validation
qualifications whenever the values are presented.

## 7. Quantitative v1.0-to-v2 Release Comparison

| Measure | V1.0 immutable Git tag | V2 source baseline | V2 frozen public-review candidate |
| --- | ---: | ---: | ---: |
| Git blobs or regular files | 407 Git blobs | 462 Git blobs | 351 regular files |
| Blob or file bytes | 120,664,617 | 121,153,124 | 35,754,807 |
| Git identity | Commit `0fa94ec...`; tag `v1.0-qpathformer-enterprise` | Commit `cf9721...`; annotated source tag | Public Git identity not yet created |
| Model-derived binaries | Present in broad source snapshot | Still represented in source history | Excluded from candidate |
| Mutable registry and run state | Present in broad release material | Classified during migration | Excluded; empty portable examples retained |
| Publication inventory and complete checksum set | Not equivalent to current v2 freeze process | Export inputs defined | Present and independently reproduced |

The v2 source baseline changed 66 files relative to the v1 tag, with 11,782
insertions and 320 deletions. The net source-baseline increase is 55 files.
Most additions implement authorization, package sealing, exporter controls,
schemas, tests, provenance, and gated release records. The smaller public
candidate is intentional and results from exact allowlisting and asset
exclusion, not loss of the three-path architecture.

## 8. Functional Differences From v1.0

### 8.1 Authorization

V1.0 demonstrated lifecycle review, promotion, freeze, and registry handling.
V2 makes training permission a separate signed artifact with:

- A named scope.
- A dataset version and source digest.
- A registry entry identity.
- A human reviewer and decision source.
- An issue time and expiry.
- An Ed25519 signature verified through an external trusted public key.

### 8.2 Package Integrity

V2 adds a second Ed25519 trust role for package sealing. The package seal binds
every regular package member except the self-referential seal file, records
path, size, and SHA-256, and signs a deterministic Merkle root. Exact inventory
reconstruction detects later additions and removals.

### 8.3 Lifecycle Failure Semantics

V2 distinguishes selection, technical eligibility, human authorization, and
execution permission. Held operations do not emit authoritative-looking
freeze artifacts or mutate registries.

### 8.4 Release Reproducibility

V2 adds:

- Exact public-copy and source-baseline allowlists.
- Hash verification before export writes.
- Path traversal, non-empty target, `.git`, symlink, and reparse-point
  rejection.
- Historical-byte preservation and controlled active-text normalization.
- Exact dependency locks and immutable CI action references.
- A publication inventory, build report, checksum set, and canonical tree
  digest.
- Separate external records for release authority and gate decisions.

### 8.5 Evidence Qualification

V2 retains v1.0 execution evidence but narrows its interpretation. Historical
LoRA loss demonstrates only execution continuity. Historical CSC scores remain
sparse, provisional, and non-certifying. The Path 3 bundle defect is disclosed
rather than rewritten.

### 8.6 CSC Direction

V2 records a separate governance snapshot and scoring contract that requires
version and hash binding, observation status, no implicit cross-version
blending, historical non-retroactivity, and future calibration. This contract
is a design baseline, not an active scorer or a new v2 CSC result.

## 9. M12 Remediation Results

The initial M12 technical review found three release-surface issues. The Human
Release Authority authorized only their correction and the required M10/M11
rebuild.

| Finding | Correction | Corrected result |
| --- | --- | --- |
| M12-F01 | Changed the custom SPDX metadata to `LicenseRef-QPATHFORMER-PLATFORM-1.0`; substantive licence terms remained unchanged. | `PASS` |
| M12-F02 | Removed mutable remote pipe-to-shell model installation guidance. | `PASS` |
| M12-F03 | Pinned `actions/checkout` v4.3.1 and `actions/setup-python` v5.6.0 to reviewed full commit SHAs. | `PASS` |

The corrected M10 and M11 records passed. This remediation does not itself
constitute a new M12 human approval.

## 10. Claims Supported for APOD-TR-010

The evidence supports these bounded statements:

- Q-Pathformer Enterprise v2 preserves the three-path architecture while
  adding fail-closed lifecycle enforcement.
- The reference implementation separates technical eligibility from explicit
  human training authorization.
- Training authorization is scope-, time-, dataset-, and registry-bound and
  is authenticated with Ed25519.
- Package integrity is bound through a separate Ed25519 key, complete sorted
  member inventory, SHA-256, and deterministic Merkle root.
- Migration creates an authorized and sealed copy without changing the
  historical source package.
- The v2 public tree was deterministically exported from an immutable source
  anchor and frozen with an independently reproduced inventory and checksum
  set.
- Twenty-four automated tests exercised authorization, sealing, lifecycle, and
  export controls with 23 passes, one environment-guarded skip, and no failure.
- Historical v1.0 path and CSC records are retained with stronger provenance,
  coverage, and claim qualifications.

## 11. Claims Not Supported

The current evidence does not support these statements:

- V2 is certified, accredited, independently assured, or production-ready.
- A signature establishes the legal identity or organizational authority of a
  signer by itself.
- A package seal approves, certifies, or makes package content safe.
- A `STATE_1` package authorizes training without a valid signed authorization.
- V2 improves TinyLlama or another model's quality.
- A new v2 GPU fine-tune has completed.
- A new v2 CSC score or Assurance Record has been generated.
- The historical CSC levels are directly comparable across sectors without
  calibration and evidence-density controls.
- The v2 candidate has passed final human release review.
- A public v2 commit, public tag, ZIP, push, asset, or publication exists.

## 12. Remaining Binding Work

Before the final APOD-TR-010 paper is published, the record still requires:

1. A separately authorized M12 human review of the corrected M11 candidate.
2. An authorized public commit and tag.
3. An authorized ZIP and independent asset checksum, if a ZIP is selected.
4. Post-push and post-download verification.
5. A final publication attestation.
6. Replacement of remaining controlled placeholders in the paper.

Platform Licence 1.1 is being prepared separately for legal review. Unless it
is later approved and adopted through a newly authorized release cycle, the
current candidate remains governed by Platform License 1.0.

## 13. Primary Evidence Records

| Record | Purpose |
| --- | --- |
| `planning/migration/V2_SOURCE_BASELINE_RECORD.json` | M05 source identity and verification. |
| `M06/V2_EXPORT_REHEARSAL_REPORT.json` | Deterministic two-target export. |
| `M07/V2_M07_CONTROLLED_TARGET_EXPORT_REPORT.json` | Controlled target creation. |
| `M08/V2_M08_V1_CSC_EVIDENCE_QUALIFICATION_REPORT.json` | Historical CSC selection and qualifications. |
| `M09/V2_M09_CANONICAL_EQUIVALENCE_RESOLUTION_REPORT.json` | Historical vendor equivalence and v2 scoring boundary. |
| `M10/V2_M10_RERUN_AFTER_M12_REMEDIATION_REPORT.json` | Corrected pre-seal verification. |
| `M11/V2_M11_REBUILD_AFTER_M12_REMEDIATION_REPORT.json` | Corrected frozen candidate identity. |
| `M12/M12_REMEDIATION_AUTHORIZATION_20260718.md` | Exact bounded remediation authority. |
| `release/PUBLICATION_INVENTORY.json` | Frozen pre-record file inventory. |
| `release/SHA256SUMS.txt` | Final per-file checksum set. |

These records support drafting. Final publication identifiers remain subject
to later human-authorized gates.
