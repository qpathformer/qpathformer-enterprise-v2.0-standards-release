# Q-Pathformer Enterprise v2.0 Standards Edition

**Fail-closed dataset lifecycle controls, operation-specific authorization, complete package sealing, and verifiable execution evidence.**

> [!IMPORTANT]
> This repository is a standards-exploration reference. It is not a trained-model distribution, a certification or conformity-assessment program, a legal approval, or an authorization for production use or deployment.

## Overview

Q-Pathformer Enterprise v2.0 provides a compact reference implementation and evidence set for the control method described in **APOD-TR-010** and the verification account reported in **APOD-TR-010-R**.

The release focuses on a specific governance problem: a dataset may be technically prepared without being authorized for a particular operation. The implementation therefore separates:

1. dataset selection and lifecycle readiness;
2. a recorded human decision for one named scope;
3. package-integrity verification; and
4. execution-time permission checks.

A favorable result at one boundary does not silently grant authority at another boundary.

## Control Model

```text
Prepared dataset
  -> operation-specific authorization
  -> separately signed package seal
  -> execution-time verification
  -> dry-run evidence or fail-closed rejection
```

The following distinctions govern interpretation of this release:

- **Readiness is not permission.** Lifecycle state, freeze status, registry presence, or a prior run does not independently authorize a new operation.
- **Single-scope is not single-use.** An `ALLOW` record contains exactly one authorized scope. A `DENY` record contains no authorized scopes. The current contract does not implement one-time consumption or replay prevention.
- **Authentication is not authority.** A valid signature authenticates the recorded object against a supplied key; it does not establish the signer's legal, professional, or organizational authority.
- **Integrity is not suitability.** A valid package seal binds the package inventory and bytes; it does not establish rights, content quality, safety, compliance, or fitness for purpose.
- **Rejection is an expected control outcome.** Negative-path cases are retained as evidence that specified invalid or mismatched inputs do not proceed through the tested endpoint.

## Verification Snapshot

| Evidence | Recorded result | Bounded interpretation |
|---|---:|---|
| September 2026 unit suite | 48 tests: 47 passed, 1 skipped, 0 failed | The skipped symbolic-link case remained environment-dependent in the retained full-suite run. |
| Synthetic command-line rehearsal | 9 of 9 expected outcomes matched | Includes four intentional rejection cases and a permitted dry run. |
| Rehearsal input | 4 synthetic records in a prepared `STATE_1`, freeze, and registry fixture | Tests authorization, package sealing, routing, and runner boundaries rather than the complete three-path lifecycle. |
| Model execution | No model training | The successful path produces dry-run evidence, including a model stub, not trained weights. |
| Historical comparison | v1.0 execution and July v2 candidate records retained separately | Historical evidence is not relabelled as a new v2 result. |

These results are evidence for the named implementation, fixtures, source selection, and recorded environment. They are not a percentage measure of production coverage or security assurance.

## Standards Papers

| Paper | Purpose |
|---|---|
| **APOD-TR-010** | Implementation report and reusable evidence-bound transition protocol. |
| **APOD-TR-010-R** | Verification results, v1.0 comparison, reproduction guidance, and evidence limits. |

The release copies are provided as PDF documents. The selected filenames and reading order are recorded in the [research-paper index](docs/research/README.md). Word source files, superseded manuscripts, and internal QA renderings are not part of the public paper set.

## Included Scope

This repository includes the release-selected implementation and documentation needed to inspect the v2.0 standards contribution, including:

- lifecycle, authorization, migration, package-sealing, and local runner entry points;
- versioned schemas and configuration;
- synthetic fixtures, unit tests, and the bounded rehearsal harness;
- retained technical evidence and provenance records;
- the compact APOD-TR-010 paper pair;
- preserved Access-PoD standards and Q-Pathformer architecture references; and
- the three-path repository topology inherited from the v1.0 enterprise release.

The three path directories preserve the wider architecture and its documentation surface. This compact edition does not republish the historical populated datasets, model outputs, or complete path runs from v1.0.

### Current endpoint boundary

The current preparation, copy-migration, and local research-runner endpoints enforce the scope:

```text
validation_parameter_update
```

Other names retained in the scope vocabulary do not establish implemented production-training, external-provider, model-release, or deployment endpoints.

## Explicit Non-Claims

This release does not claim or provide:

- a new trained Q-Pathformer model, model weights, or model-quality benchmark;
- a new GPU fine-tuning result;
- a complete replay of the v1.0 three-path enterprise lifecycle;
- a new CSC score or completed CSC Assurance Record;
- production-training, external-provider, model-release, or deployment authorization;
- independent security, cryptographic, legal, or conformity assurance;
- automated legal approval, professional credential verification, or organizational authority; or
- complete key-management, revocation, trusted-timestamp, confidentiality, or availability infrastructure.

The detailed boundaries and supporting evidence are stated in the two standards papers.

## Review and Reproduction

### Read-only review

Start with:

1. the [documentation index](docs/README.md);
2. the [research-paper index](docs/research/README.md);
3. the [v2.0 release notes](docs/release/V2_STANDARDS_RELEASE_NOTES.md); and
4. the [provenance index](release/provenance/README.md).

The retained evidence may be reviewed without rerunning the implementation.

### Bounded local rehearsal

For a new local rehearsal, use the complete prepared workspace, **Python 3.11**, and the pinned lightweight dependencies. Follow:

- [TR010 Standards Reference Runbook](docs/execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md)
- [Local Checks](docs/execution/LOCAL_CHECKS.md)

The current route uses temporary synthetic data. It does not call Ollama, load `gpt-oss:20b`, download TinyLlama, use private datasets, execute a GPU fine-tune, or calculate a CSC score.

> [!CAUTION]
> `tools/verify_private_workspace.py` checks the selected workspace and its exact, registered two-PDF standards selection. Its `--require-final-papers` mode verifies both PDF identities before owner sealing. This bounded preparation check is not a generic public-package security audit or publication permission. The two standards papers alone are insufficient to reproduce the executable route.

A later run must be recorded as a new observation. Do not merge it into the retained September totals, overwrite earlier evidence, or copy an earlier PASS into a new result.

## Repository Map

| Path | Role in this edition |
|---|---|
| [`docs/`](docs/) | Architecture, execution guidance, papers, legal-review context, and release records. |
| [`scripts/`](scripts/) | Lifecycle, authorization, migration, package-integrity, and runner entry points. |
| [`shared/`](shared/) | Schemas, configuration, model references, and preserved standards material. |
| [`path_1_tr_corpus_reference/`](path_1_tr_corpus_reference/) | TR corpus reference path structure and documentation. |
| [`path_2_access_mode_canonical/`](path_2_access_mode_canonical/) | Access-Mode path structure and documentation. |
| [`path_3_external_custom_adapter/`](path_3_external_custom_adapter/) | External/custom adapter path structure and documentation. |
| [`tests/`](tests/) | Synthetic fixtures and unit checks. |
| [`tools/`](tools/) | Workspace checking and bounded rehearsal tooling. |
| [`evidence/`](evidence/) | Dated technical evidence, environment records, and source ledgers. |
| [`release/`](release/) | Paper selection, provenance, relocation, and release-control records. |

The repository layout follows the broad structure of the [Q-Pathformer Enterprise v1.0 release](https://github.com/qpathformer/qpathformer-enterprise-v1.0-release/releases/tag/v1.0-qpathformer-enterprise). The current `docs/research/` directory serves the paper-and-results role previously carried by `docs/orientation/`; a duplicate orientation directory is not required. See [Repository Layout](docs/REPOSITORY_LAYOUT.md).

## Evidence Periods and Provenance

The release preserves distinct evidence periods rather than presenting them as one continuous experiment:

| Evidence period | Role |
|---|---|
| **April 2026 v1.0 execution** | Historical three-path, local model-run, and qualified CSC observations. |
| **July 2026 v2 candidate work** | Historical deterministic export, candidate verification, findings, remediation, and preserved human-disposition boundary. |
| **September 2026 v2 controls** | Current synthetic authorization, package-integrity, routing, and dry-run verification evidence. |
| **Publication records** | Documentary selection, provenance, and release binding; not additional runtime evidence. |

The [History and Provenance Notice](history_notice.md) and [provenance index](release/provenance/README.md) describe these boundaries. Historical records retain their original conclusions and identities. A later manuscript, relocated file, or release asset does not retroactively change the object or decision recorded by an earlier ledger.

Supporting release-maintenance records include:

- [V2 Standards Cleanup Record](docs/release/V2_STANDARDS_CLEANUP_20260906.md)
- [Relocation Index](release/provenance/RELOCATION_INDEX_20260906.json)
- [Paper Release Selection](release/PAPER_RELEASE_SELECTION.json)
- [Publication Handoff](docs/release/V2_STANDARDS_PUBLICATION_HANDOFF_20260906.md)
- [Final PDF Registration](docs/release/V2_STANDARDS_PDF_FINALIZATION_20260906.md)

## Governance and Legal Boundary

No actual lawyer review is recorded for this release. The [illustrative legal-review worked example](docs/legal-review/ILLUSTRATIVE_LEGAL_REVIEW_WORKED_EXAMPLE.md) is fictional, remains on `HOLD_PENDING_REAL_REVIEW`, and is not consumed by the runtime.

Under the proposed project profile, qualified human review of identified legal questions and organizational authorization of a named operation remain separate responsibilities. AI assistance may support inventory, comparison, and drafting, but it is not the required human decision and does not confer permission.

## Shared Components

`shared/models/` contains architecture reference material, not trained weights or evidence of a new v2 model evaluation. Any unpopulated evaluation interface remains an interface, not a completed evaluation result.

`shared/standards/` contains the documented Access-PoD v1a text subset, enterprise schemas, profiles, and mapper definitions selected for this repository. It is not a complete upstream publication pack and does not create a new CSC score or certification state.

## Version Relationship

| Version | Position |
|---|---|
| **Q-Pathformer Enterprise v1.0** | Published historical three-path foundation and execution evidence. |
| **Q-Pathformer Enterprise v2.0 Standards Edition** | Current compact standards-exploration release focused on explicit authorization, package integrity, fail-closed controls, and bounded verification. |
| **Q-Pathformer Enterprise v3** | Planned full enterprise reproduction combining the three-path foundation with the v2 control model within a separately defined scope. V3 is not included in this release. |

Future CSC Assurance Record work remains separately scoped and is not made operational by publishing v2.0.

## Release Identification

```text
Repository: qpathformer/qpathformer-enterprise-v2.0-standards-release
Release tag: v2.0-qpathformer-enterprise-standards
```

The owner will bind the selected publication assets and release-integrity records through the final GitHub release record; local PDF registration does not assert that publication has occurred. Earlier editorial handoffs and historical ledgers remain preserved rather than being rewritten to match later publication files.

## Licence and Notices

Use and redistribution are governed by the repository's current legal and attribution files:

- [LICENSE](LICENSE)
- [QPATHFORMER-PLATFORM-1.0.txt](QPATHFORMER-PLATFORM-1.0.txt)
- [NOTICE.md](NOTICE.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

These files should be read together. Historical notices remain historical records and do not independently create current publication or operational authority.
