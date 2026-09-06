# Final PDF Registration - V2.0 Standards Edition

Date: 6 September 2026. Scope: publication metadata and current navigation only.

## Selected Papers

The owner-exported PDFs remain byte-for-byte unchanged. No manuscript revision suffix, PDF re-export, Word edit or replacement paper was created by this finalization.

| File in `docs/research/` | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `APOD-TR-010_STANDARDS_REVIEW.pdf` | 43 | 358,864 | `61fc5a19e19a963f3d5754daf0f5dc53d1f2d5b116078e29f2f180458bc35fe0` |
| `APOD-TR-010-R_STANDARDS_REVIEW.pdf` | 30 | 310,093 | `59984745b80eeacfcb1b872375e8dbf4dd1f7bbd0790c1f39bbd10f0f17f0db6` |

All 73 exported pages were visually reviewed in the preceding read-only review on this date. No blocking layout defect was found, and all page text matched the corrected QA text after whitespace normalization. The visual review is not a full PDF security audit, legal review or release authorization.

The [paper selection](../../release/PAPER_RELEASE_SELECTION.json) and [document allowlist](../../release/provenance/DOCUMENT_ALLOWLIST.json) bind these exact publication bytes. Prior DOCX and internal QA-PDF hashes are not used as substitutes.

## Bounded Changes

- Updated the current root/documentation/research indexes and publication guidance to describe the existing PDFs, with live PDF links.
- Corrected excess Markdown escaping in the repository-layout document without changing folder names or its substantive organization.
- Replaced stale current links to external editorial files with the explicit archive references below.
- Registered the PDF pair and changed only the two accepted filename constants in `tools/verify_private_workspace.py`. Its identity checks, exact-pair restriction, rejection behavior and historical private-document mode remain intact.
- Retained preceding Word-source identities as explicitly historical metadata, not as a claim that those older bytes were the final conversion sources.

Hash comparison confirmed 332 existing files unchanged, including both PDFs and every existing file outside the eleven-file edit selection. This record is the only added release file, giving 344 files. Historical source inventories, the relocation index, evidence logs, vendor bytes, `history_notice.md`, licences and notices were not rewritten.

## External Editorial Locators

These are owner-local archive references, not bundled release companions or public download links. `owner_local_all_records` denotes the owner's existing external `all records` archive.

| Archive-relative locator | Bytes | SHA-256 |
|---|---:|---|
| `standards_cleanup_20260906/docs/research/TR010_R02_EDITORIAL_HANDOFF.json` | 5,663 | `4f3559ea86416f84ef3d536177106e141bccee2f9ff63cb373b4be059a275892` |
| `standards_cleanup_20260906/docs/research/TR010_R02_FINAL_ADJUSTMENTS_20260906.md` | 4,345 | `d36323a1730e1b0ad24c882a6eb2d372aeae8418d0dddd700b08949099a3a0e2` |
| `v2 standards papers/TR010_FINAL_EDITORIAL_CHANGES_20260906.md` | 4,068 | `cf491ca6c8a0113bf98e791eb02b0f191926c9ba9d0a1d9e249a4100e34f386e` |

The earlier handoff and edit records retain their original scope. Historical locators inside the papers are not silently rewritten to describe the new PDFs. The preceding relocation index is also preserved, rather than retrospectively modified to include later archival actions.

Pre-edit copies of the eleven updated files and the pre-edit full-tree inventory are retained under owner-local archive identifier `standards_pdf_finalization_20260906`. Working validation reports for this finalization are retained there separately from the release selection.

## Verification

The applied change passed the following local checks on 6 September 2026:

| Check | Result |
|---|---|
| `verify_private_workspace.py --require-final-papers` | PASS; both final PDFs registered and hash-matched; zero errors. |
| Unit suite | 56 passed, zero skipped, zero failed; 2.285 seconds. |
| Windows symbolic-link rejection test | Passed in this new full-suite run. |
| Synthetic CLI rehearsal | PASS; 9/9 expected outcomes, including four intentional rejections; no model training. |
| Updated Markdown navigation | No missing local link target in the nine updated/added Markdown files. |
| PDF and historical preservation | No unexpected file changes; both PDF hashes unchanged. |

The separate rehearsal timestamp is `2026-09-06T20:22:15.011777+10:00`, as recorded by the harness. The final-paper output, unit log, rehearsal JSON and preservation/navigation comparison are retained under the external archive identifier above. These are new local observations; they do not replace the papers' retained 48-test, 47-pass, one-skip result or any historical milestone. Hosted GitHub CI was not run by this finalization.

Use the [local checks](../execution/LOCAL_CHECKS.md) to verify the registered PDF pair and the current unit suite. Rehearsal reports use a unique path outside the release; the rehearsal is synthetic and performs no model training.

The papers describe an earlier inspected private-drafting checker and dated test totals. The current checker also has the documented exact-PDF preparation mode. Current metadata and fresh verification remain separate from those historical implementation observations.

## Owner Handoff

After successful final checks and the owner's applicable selection/notice review, the folder can proceed to owner ZIP/sealing using the [publication handoff](V2_STANDARDS_PUBLICATION_HANDOFF_20260906.md). The broad three-path folder structure is retained; no new layout or full enterprise dataset is required for this compact standards scope.

Finalize file inventory/checksums before creating the archive. Keep the ZIP and its final SHA-256 sidecar outside the project folder. If the owner's sealing tool already provides the inventory, checksums and archive verification, do not duplicate that process. Neither a ZIP nor a bare hash alone authenticates a signer or grants rights.

No new July milestone, legal clearance, licence adoption, Git commit/tag, archive, remote push or publication is established by this record. V2.0 is the current Standards Edition; v3 remains planned.
