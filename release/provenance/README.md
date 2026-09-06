# Portable Provenance Index

These records remain available in the local standards pack and are prepared for Git. Preservation does not grant publication permission. Historical records can contain original absolute paths; review sharing suitability without silently altering their bytes.

## Current Selection

- [Paper selection](../PAPER_RELEASE_SELECTION.json): exactly two final owner-exported PDFs, registered by path, size and SHA-256. Word sources remain external; preceding Word identities are historical, not asserted conversion bindings.
- [Document allowlist](DOCUMENT_ALLOWLIST.json): the exact registered PDF pair. Missing, changed or unselected documents fail the applicable checks.
- [Cleanup and relocation index](RELOCATION_INDEX_20260906.json): every archived file by relative path, bytes and hash; includes earlier manuscript locator aliases.
- [Cleanup record](../../docs/release/V2_STANDARDS_CLEANUP_20260906.md): source-tree comparison, file moves, checker adjustment and verification limits.
- [Final PDF registration](../../docs/release/V2_STANDARDS_PDF_FINALIZATION_20260906.md): unchanged publication PDFs, bounded metadata changes and externally preserved editorial locators. The earlier R02 handoff is not bundled; its dated source/QA identities do not identify the final PDF bytes.
- [History notice](../../history_notice.md): original HN-20260905-R03 chronology, not a new release approval.

## Source and Historical Records

| Record or folder | Interpretation |
|---|---|
| `SOURCE_ANCHORS.json` | Source commit/tag/tree and corrected candidate identities. |
| `SOURCE_SELECTION.json` | Initial copied files, source/destination hashes and immutable treatment. |
| `SOURCE_CATALOGUE.json`, `EXCLUSIONS.json` | Initial source inventory and excluded material, not the present folder census. |
| `EXTERNAL_REFERENCES.json` | External papers and legal-review drafts by identity; not adopted contents. |
| `GENERATED_FILES.json` | Initial preparation-file identities, not current hashes after later edits. |
| `STANDARDS_SUBSET.json` | Preserved vendor files, physical hashes and canonical comparisons. |
| `PRIVATE_BASELINE_AUTHORITY.json`, `PRIVATE_BASELINE_DELTA.json` | Bounded private-baseline history, not public-release authority. |
| `historical_candidate/`, `historical_records/` | Original July candidate, review, remediation and drafting evidence. |
| `historical_seals/` | Earlier seal manifests/checksums; not a seal of this standards tree. |
| `standards_consolidation_20260905/` | Captured source tree and point-in-time consolidation records. |
| `development_slices/` | Dated source/editorial changes. Later paper identities do not rewrite them. |

The 6 September cleanup does not modify source inventories, historical candidate/record/seal bytes, development-slice identities or the v1a vendor subset. The current paper selection and technical document allowlist are updated, with their prior bytes preserved in the archive.

Some records reference earlier `docs/research/tr010/` manuscripts or editorial work that is no longer bundled. Use the relocation index and recorded hashes, not a claim that every old relative path exists in this release. External archive availability is not the same as public distribution.

## Historical Link Scope

Links in preserved history notices, earlier preparation notes and July planning records retain their original context. Some name excluded Word manuscripts or planning files; others retain the relative directory depth of an earlier layout. These links are historical locators, not the current execution route or a promise that every target can be opened from this compact pack.

For an archived editorial object, consult the [relocation index](RELOCATION_INDEX_20260906.json), its locator aliases and recorded hash. For another historical source, consult the source records above and the identified external source. If an object is not indexed or available, report that limit rather than substituting a similarly named file or assuming equivalent evidence. Preserved records are not edited merely to make their old links look current.

The live [paper index](../../docs/research/README.md) and [reference runbook](../../docs/execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md) identify the current selected PDFs and bounded reproduction route. The [validation evidence](../../evidence/v2_validation/README.md) and [private-baseline records](../private_baseline/README.md) are populated, dated supporting records, not new permissions.

A matching hash establishes file identity, not ownership, independent assurance, legal entitlement or permission for a named operation.
