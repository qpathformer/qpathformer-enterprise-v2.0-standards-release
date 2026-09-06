# Standards Consolidation Evidence

This directory records the local consolidation of 2026-09-05. It is not legal review or release approval.

- `unit_tests.txt` records the unchanged application suite run in the selected tree, including any environment skip.
- `rehearsal.json` records the nine-step isolated CLI rehearsal and its actual source hashes. It is separate from the fictional legal-review record.
- `workspace_verification.json` records layout-policy, syntax/schema, document allowlist and historical-copy checks.
- `manuscript_verification.json` records source/final manuscript hashes, 12 manual changes, 162 contents changes, 178 matching page references and unchanged non-TOC body text during the Word save.
- `word_refresh.json` records the individual checked contents references and stabilized 380-page result.
- `selection_checks.json` records preserved source groups, illustrative record binding and local link checks.

## Observed Results

The existing suite ran 48 tests: 47 passed, one Windows symlink-capability test was skipped, and none failed. The CLI rehearsal returned all nine expected outcomes. The source check compared all 271 captured original files and confirmed 199 protected source copies unchanged. All 62 checked active local documentation links resolved. The synthetic material hash and non-approval fields matched their declared example boundary.

Word exported and the supplied DOCX renderer rasterized all 380 pages. All 178 checked contents page references matched their bookmarks, with stable pagination; no main-document placeholder or bookmark/reference error text remained. Word's save did not alter any non-TOC body text after the recorded manual edits.

Visual inspection covered pages 1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 284, 285, 286 and 380. The source-note heading was kept with its first reference, followed by a full rerender and a further check of pages 285-286. The inspected pages were readable without observed clipping or overlap. The inherited contents opening whitespace was retained rather than redesigning the paper.

This is a targeted visual check plus whole-document automated text/contents checks, not a claim that every page received independent visual or substantive peer review. Author review, full editorial acceptance and actual legal review remain distinct from manuscript assembly and pagination completion. QA PDFs/PNGs remain outside the repository selection.

No real model training, network inference, complete three-path replay, new CSC score or hosted CI result is claimed. Temporary rehearsal keys are discarded. See the [consolidation record](../../../docs/release/LOCAL_STANDARDS_CONSOLIDATION_20260905.md).
