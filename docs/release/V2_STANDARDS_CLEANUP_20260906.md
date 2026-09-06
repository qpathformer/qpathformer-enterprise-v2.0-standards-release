# V2 Standards Local Pack Preparation

Date: 6 September 2026. Scope: reviewer navigation, redundant-file archiving and PDF-only paper selection before owner sealing. This is not a new M milestone, release seal or publication authorization.

## Historical Layout Comparison

The public [TR008-TR009 v1.0 release](https://github.com/qpathformer/qpathformer-enterprise-v1.0-release/releases/tag/v1.0-qpathformer-enterprise), its tag target `0fa94ecf47d698a894bc868545f110570d0dec50`, repository tree, root README and docs README were inspected through the GitHub connector. The release's sealed ZIP was not downloaded or audited.

V1.0 separates architecture, execution and orientation and retains three path roots plus `scripts/` and `shared/`. V2 already had those core interfaces. Its existing `docs/research/` has the orientation role; adding or renaming another folder would create needless path changes. The [layout comparison](../REPOSITORY_LAYOUT.md) explains the retained structure and narrower reproduction scope.

## Archive Selection

240 files, 52,074,369 bytes, were moved from the release to the owner's existing records location, under the collision-safe batch `standards_cleanup_20260906`. Every transferred file was checked by pre-move size and SHA-256. No file was deleted or overwritten at the destination.

The batch is under `C:\qpathformer_enterprise_v2\all records`. The [portable relocation index](../../release/provenance/RELOCATION_INDEX_20260906.json) records original and archived relative paths, hashes and historical manuscript locator aliases.

Archived contents are superseded manuscripts, editorial helpers and rendering files, the two current R02 Word conversion originals, and five obsolete private-development/future-release instruction files. Earlier active-file bytes are preserved separately under the batch's `before_edits/` directory.

Historical candidate/records/seals, source inventories, September technical evidence, existing standards/vendor files, licence texts, dependency pins and lifecycle/authorization scripts remain in place. They are not redundant merely because they are older. No directory was renamed and no new directory was created inside the release.

## Current Documentation and Paper Format

Root and docs navigation now identify the compact R02 paper pair, not the former 380-page main paper. Architecture and path READMEs explain which interfaces remain unpopulated and why. The existing research folder has a PDF-only index. Paper filenames remain explicit, not broken links to nonexistent exports.

The [paper selection](../../release/PAPER_RELEASE_SELECTION.json) names exactly two final PDF paths. Both are **pending owner conversion and review**. Word originals and earlier QA PDFs are not release contents. The R02 editorial handoff and adjustment record remain unchanged as dated evidence; their archived items resolve through the relocation index.

## Limited Checker Update

Only the local preparation checker and its document-allowlist tests changed in executable code. The new PDF scope allows exactly the selected pair by registered path, size and SHA-256. An empty allowlist means pre-conversion preparation; it does not mean that a zero-paper release is complete. Word files, unknown PDFs, incomplete registrations and altered bytes are rejected.

`--require-final-papers` fails until both final PDFs are registered, present and hash-matched. The existing legacy private-draft checker mode remains supported for its original tests. PDF checking covers identity and a basic file envelope only; visual review, compressed content and comprehensive PDF safety remain separate.

The runbook now explicitly selects Python 3.11, already its documented requirement. Its synthetic execution steps and authorization semantics are unchanged. No runtime lifecycle control, schema, signing rule, model or dependency was changed. These are housekeeping checks, not new release gates.

## Verification and Remaining Work

The cleanup regression run completed **56 tests: 56 passed, zero failures, zero skips**. This includes eight new PDF-selection tests and the existing Windows capability test. It is separate from the dated 48-test suite and operator-reported follow-up described in the papers. Those historical records and manuscript claims were not rewritten.

The source-preparation checker passed. Its final-paper mode returned the expected `final_pdf_pair_not_registered` failure while owner exports are pending. The machine-readable [local preparation check](../../release/LOCAL_PACK_PREPARATION_20260906.json) records preservation, navigation and new test evidence. The existing nine-step CLI rehearsal was not rerun; no model training or new CSC score was generated.

Before sealing, complete owner PDF conversion and visual review, register exact PDF bytes, rerun the final-paper check and confirm the applicable rights disposition and exact publication selection. Then the owner can inventory/checksum/seal that completed selection. No Git initialization, commit, tag, ZIP, push or publication was performed by this cleanup.
