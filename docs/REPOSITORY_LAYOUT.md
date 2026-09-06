# Q-Pathformer Enterprise v2.0 Standards Edition - Repository Layout

This document describes the public repository organization for the **Q-Pathformer Enterprise v2.0 Standards Edition**.

The layout preserves the established three-path Q-Pathformer structure while separating current v2.0 implementation, bounded synthetic verification, historical evidence, publication records, and planned v3 work.

> [!IMPORTANT]
> Repository location does not determine authority. A file placed in a lifecycle, evidence, release, standards, or frozen directory does not become approved, authorized, verified, or suitable merely because of its path or name.

## Layout Principles

The repository follows six principles:

1. **Preserve established interfaces.** The three `path_*` directories, `scripts/`, and `shared/` retain their established names because implementation and documentation refer to them.
2. **Keep current and historical evidence separate.** April v1.0 evidence, July v2 candidate records, September v2 control verification, and publication records remain distinct evidence periods.
3. **Separate human-readable documentation from machine-readable release control.** `docs/release/` contains explanatory release documents; root `release/` contains selection, provenance, and release-control records.
4. **Do not duplicate documentation roles.** `docs/research/` carries the paper-and-results role that `docs/orientation/` served in v1.0.
5. **Do not rewrite historical records to match a new layout.** A dated path in a preserved record remains evidence of the earlier object and location.
6. **Keep v3 outside the v2 release boundary.** Full enterprise reproduction is planned v3 work and is not implied by the v2.0 tree.

## Top-Level Structure

```text
.
├── README.md
├── docs/
│   ├── README.md
│   ├── REPOSITORY_LAYOUT.md
│   ├── architecture/
│   ├── execution/
│   ├── research/
│   ├── legal-review/
│   ├── release/
│   └── history/
├── scripts/
├── shared/
├── path_1_tr_corpus_reference/
├── path_2_access_mode_canonical/
├── path_3_external_custom_adapter/
├── tests/
├── tools/
├── evidence/
├── release/
├── history_notice.md
├── LICENSE
├── NOTICE.md
├── THIRD_PARTY_NOTICES.md
└── QPATHFORMER-PLATFORM-1.0.txt
```

The release manifest and repository tree determine the exact selected files. This document explains directory roles; it is not a substitute for the release record.

## Top-Level Directory Roles

|Path|Role in the v2.0 Standards Edition|Boundary|
|-|-|-|
|[`docs/`](./)|Architecture, execution guidance, research papers, legal-review context, history, and release documentation.|Documentation does not create runtime permission or release authority.|
|[`scripts/`](../scripts/)|Lifecycle, authorization, migration, package-integrity, and local runner entry points.|A script's presence does not establish that every named scope or production endpoint is implemented.|
|[`shared/`](../shared/)|Versioned schemas, configuration, model references, and selected standards material.|Shared references are not trained weights, a complete upstream publication pack, or a new assurance result.|
|[`path_1_tr_corpus_reference/`](../path_1_tr_corpus_reference/)|TR corpus reference path structure and stage documentation.|The compact release does not republish the complete populated v1.0 path.|
|[`path_2_access_mode_canonical/`](../path_2_access_mode_canonical/)|Access-Mode path structure and stage documentation.|Path structure is not a new end-to-end runtime execution or CSC result.|
|[`path_3_external_custom_adapter/`](../path_3_external_custom_adapter/)|External and custom adapter structure with containment-oriented documentation.|No external input is promoted or authorized merely by entering this path.|
|[`tests/`](../tests/)|Unit tests and synthetic fixtures supporting the bounded verification route.|Test coverage is limited to named cases and recorded environments.|
|[`tools/`](../tools/)|Local workspace checking and synthetic rehearsal tooling.|Private-workspace checks are not generic public-release acceptance tests.|
|[`evidence/`](../evidence/)|Dated technical observations, logs, environment records, source captures, and evidence ledgers.|Historical and current evidence must not be merged into one experiment.|
|[`release/`](../release/)|Paper selection, provenance, relocation, and release-control records.|A release-control record describes selected objects; it does not grant operational permission.|

## Documentation Layout

### `docs/architecture/`

Contains the current architecture description and technical boundaries of the v2.0 standards implementation.

Use this directory to understand:

* how lifecycle readiness, authorization, package integrity, and execution checks are separated;
* which interfaces are current;
* which capabilities remain external or unimplemented; and
* how the compact v2.0 edition relates to the broader v1.0 system.

Architecture documentation does not establish that every conceptual scope has an executable endpoint.

### `docs/execution/`

Contains the current synthetic runbook and local checking guidance.

Primary references include:

* [TR010 Standards Reference Runbook](execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md)
* [Local Checks](execution/LOCAL_CHECKS.md)

The current route uses a complete prepared workspace, Python 3.11, pinned lightweight dependencies, synthetic fixtures, and dry-run behavior. It is not a replay of the populated v1.0 three-path lifecycle.

### `docs/research/`

Contains the public paper set and its reading index.

The v2.0 Standards Edition has two release papers:

1. **APOD-TR-010**, the implementation report and reusable evidence-bound transition protocol.
2. **APOD-TR-010-R**, the verification results, v1.0 comparison, reviewer procedure, and evidence limitations.

The exact public filenames and reading order are defined in the [research-paper index](research/README.md). Word source files, superseded manuscripts, and internal QA renderings are outside the public paper set.

This directory replaces the paper-and-results function of v1.0's `docs/orientation/`. A second orientation directory is not required.

### `docs/legal-review/`

Contains the illustrative legal-review worked example and its explanatory boundary.

The example is fictional, remains on its recorded hold, and is not consumed by the runtime. It does not establish actual lawyer review, practitioner credentials, rights clearance, or organizational authorization.

### `docs/release/`

Contains human-readable release documentation, including release notes, publication handoff, and maintenance records.

Primary references include:

* [V2 Standards Release Notes](release/V2_STANDARDS_RELEASE_NOTES.md)
* [V2 Standards Publication Handoff](release/V2_STANDARDS_PUBLICATION_HANDOFF_20260906.md)

This directory explains release preparation and interpretation. The root `release/` directory contains the corresponding machine-readable selection and provenance records.

### `docs/history/`

Contains retained historical documentation where selected for the release.

Historical records preserve their original context. They are not current instructions unless another current document explicitly adopts them.

## Three-Path Structure

The three path roots remain visible because they are part of the Q-Pathformer architecture and are referenced by implementation and documentation.

|Path|v1.0 role|v2.0 Standards Edition treatment|
|-|-|-|
|Path 1|TR corpus transformation and training preparation.|Retains path structure and documentation without republishing the complete populated historical run.|
|Path 2|Access-Mode source-first and runtime signal lifecycle.|Retains path structure and current control references without claiming a new complete lifecycle traversal.|
|Path 3|External/custom input normalization and containment.|Retains adapter and containment structure without implying promotion, training permission, or model execution.|

The compact v2.0 rehearsal begins from a prepared synthetic `STATE_1`, freeze, and registry fixture. It tests the authorization, package-sealing, routing, and runner boundaries rather than rebuilding all three paths.

## Implementation and Verification Surfaces

### `scripts/`

The current implementation surface includes entry points for:

* lifecycle review and transition handling;
* explicit training-authorization creation and verification;
* authorized package preparation;
* copy-based migration;
* package inventory and sealing; and
* the local research runner.

The current preparation, migration, and local research-runner endpoints enforce `validation_parameter_update`. Other scope names retained in the vocabulary do not establish implemented production-training, external-provider, model-release, or deployment endpoints.

### `shared/`

`shared/` contains reusable schemas, configuration, reference material, and selected standards components.

* `shared/models/` contains architecture reference material, not model weights or evidence of a new v2 model benchmark.
* `shared/standards/` contains the selected Access-PoD v1a text subset, enterprise schemas, profiles, and mapper definitions retained for this release.

An empty or unpopulated interface is an interface, not evidence that an evaluation or assurance process occurred.

### `tests/`

Contains the named unit tests and synthetic fixtures used by the bounded standards verification route.

The retained September suite and rehearsal are reported in APOD-TR-010-R. A later run is a new observation and must not be merged into the retained totals or used to rewrite historical results.

### `tools/`

Contains the local checking and synthetic rehearsal harnesses.

> [!CAUTION]
> `tools/verify_private_workspace.py` checks the selected workspace and the exact registered standards PDF pair. Use `--require-final-papers` before owner sealing. Its earlier private-drafting mode remains distinct. Neither mode grants publication authority or constitutes a generic public-package security audit; do not weaken the checks to obtain PASS.

The public papers alone are insufficient to reproduce the executable route. Reproduction requires the complete selected implementation, tests, fixtures, schemas, backend profile, dependencies, and relevant provenance.

## Evidence and Provenance Separation

The repository separates technical evidence from release-control records.

### `evidence/`

Contains dated observations and supporting records, including:

* unit-test logs;
* synthetic rehearsal reports;
* environment records;
* source captures;
* historical candidate records; and
* evidence-source ledgers.

These materials preserve what was observed for an identified source and environment. They do not become current merely because they remain in the repository.

### `release/provenance/`

Contains records used to locate, interpret, and relate release-selected and historical objects.

Historical candidate, historical record, and historical seal material remains separate from current v2.0 publication records. Earlier counts, paths, and identities describe their original objects, not the entire compact release tree.

Where a preserved record names an earlier path such as `docs/research/tr010/` or a former `records/` directory, treat that path as a dated locator. Use the current provenance and relocation records to locate the selected object. Do not silently edit the historical record to make its old path look current.

### `release/private_baseline/`

Where retained, this directory records preparation history for the selected working baseline. It is not a current M11 seal, public release approval, or operational authorization.

## Public Release Boundary

The public v2.0 release excludes material that is not part of the selected standards edition, including:

* Word manuscript sources;
* superseded drafts;
* internal QA renderings;
* temporary workspaces and transient reports;
* disposable or private signing keys;
* obsolete private-development instructions;
* external workstation archives themselves, which are not bundled;
* unselected historical populated datasets and model outputs; and
* planned v3 implementation material.

Historical records and some preparation guidance retain original absolute paths or workstation archive locators. These are contextual references, not a promise that another machine has those locations. Review sharing suitability without silently changing historical bytes.

Historical references to excluded or externally preserved material remain valid as historical references. They do not promise that every named object is distributed in this repository.

The [History and Provenance Notice](../history_notice.md), [provenance index](../release/provenance/README.md), [paper-selection record](../release/PAPER_RELEASE_SELECTION.json), and [relocation index](../release/provenance/RELOCATION_INDEX_20260906.json) describe the relevant boundaries.

## Relationship to the v1.0 Enterprise Layout

The v2.0 Standards Edition preserves the broad organization of the published [Q-Pathformer Enterprise v1.0 release](https://github.com/qpathformer/qpathformer-enterprise-v1.0-release/releases/tag/v1.0-qpathformer-enterprise) while narrowing the selected content to the current standards contribution.

|v1.0 organization|v2.0 treatment|Reason|
|-|-|-|
|`docs/architecture/`|Retained|Explains the current system structure and technical limits.|
|`docs/execution/`|Retained with current synthetic guidance|Historical full-path commands are not the current compact reproduction route.|
|`docs/orientation/`|Represented by `docs/research/`|Preserves the paper/results role without duplicate folders.|
|Three `path_*` roots|Retained|Preserves established interfaces and architectural continuity.|
|`scripts/` and `shared/`|Retained|Avoids cosmetic movement that could break implementation references.|
|Populated lifecycle, model, and CSC outputs|Selected historical evidence only|Historical evidence is distinct from a new v2.0 enterprise execution.|
|Release assets and integrity records|Bound through the v2.0 release record|The repository layout document does not itself establish publication or operational authority.|

## Review Routes

### Read-only review

Recommended order:

1. [Root README](../README.md)
2. [Documentation index](README.md)
3. [Research-paper index](research/README.md)
4. APOD-TR-010
5. APOD-TR-010-R
6. [History and Provenance Notice](../history_notice.md)
7. [Provenance index](../release/provenance/README.md)

A reviewer may inspect the retained evidence without executing the implementation.

### Bounded local reproduction

Use the current runbook and local checks with the complete prepared workspace. New executions must produce new records and must retain their own environment, source selection, outcomes, failures, and skips.

Do not:

* overwrite retained evidence;
* copy a historical PASS into a new result;
* weaken a check to match an expected outcome;
* present the bounded workspace/PDF preparation checker as a generic public-package security verifier; or
* describe the synthetic rehearsal as a full v1.0 or planned v3 enterprise replay.

## Version Boundary

|Version|Repository-layout position|
|-|-|
|**Q-Pathformer Enterprise v1.0**|Published historical three-path foundation, populated execution examples, and qualified historical evidence.|
|**Q-Pathformer Enterprise v2.0 Standards Edition**|Current compact standards release focused on explicit authorization, package integrity, fail-closed controls, and bounded synthetic verification.|
|**Q-Pathformer Enterprise v3**|Planned full enterprise reproduction combining the three-path foundation with the v2 control model under a separately defined scope. V3 is not part of this repository.|

Future CSC Assurance Record work remains separately scoped. Its possible future relationship to v3 does not make it an implemented v2 capability.

## Layout Change Control

Changes to established paths should be deliberate because scripts, tests, paper locators, and provenance records may depend on them.

A layout change should therefore:

1. identify the affected current paths;
2. update live documentation and executable references together;
3. preserve historical records without rewriting their original locators;
4. update release selection and provenance records for the new objects;
5. rerun the applicable checks; and
6. record the change as a new release-layer identity.

Do not rename top-level directories solely for presentation during a release-finalization pass. Structural refactoring belongs in a separately scoped development change, not in a documentation-only publication adjustment.

## Related Documents

* [Root README](../README.md)
* [Documentation index](README.md)
* [Research-paper index](research/README.md)
* [TR010 Standards Reference Runbook](execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md)
* [Local Checks](execution/LOCAL_CHECKS.md)
* [V2 Standards Release Notes](release/V2_STANDARDS_RELEASE_NOTES.md)
* [V2 Standards Publication Handoff](release/V2_STANDARDS_PUBLICATION_HANDOFF_20260906.md)
* [History and Provenance Notice](../history_notice.md)
* [Provenance index](../release/provenance/README.md)
* [Paper-selection record](../release/PAPER_RELEASE_SELECTION.json)
