# V2 Standards Publication Handoff

Date: 6 September 2026. Current scope: local standards-file preparation, not a completed GitHub publication, legal clearance or reopening of July milestones.

## Fixed Designation

- Repository: `qpathformer/qpathformer-enterprise-v2.0-standards-release`.
- Tag: `v2.0-qpathformer-enterprise-standards`.
- Title: **Q-Pathformer Enterprise v2.0 Standards Edition**.
- Edition date: **6 September 2026**.
- Designated [v2 release link](https://github.com/qpathformer/qpathformer-enterprise-v2.0-standards-release/releases/tag/v2.0-qpathformer-enterprise-standards).
- Prepared [release notes](V2_STANDARDS_RELEASE_NOTES.md).

These are assigned names, not proof of remote publication or an immutable Git binding. This cleanup checked the historical v1.0 release, not the availability of the v2 destination. The private development repository is not renamed or made public.

Suggested annotated-tag message:

```text
Q-Pathformer Enterprise v2.0 Standards Edition

APOD-TR-010 method/protocol paper and APOD-TR-010-R results paper,
distributed as two PDFs with reference implementation, synthetic
reproduction guidance and preserved evidence/provenance records.

Bounded standards exploration, not full enterprise reproduction,
automated legal approval, independent certification or a new CSC score.
```

## Selected Papers

The [paper index](../research/README.md) links the two final PDFs. [PAPER_RELEASE_SELECTION.json](../../release/PAPER_RELEASE_SELECTION.json) records their exact filenames, sizes and SHA-256 values. All 73 exported pages were visually reviewed. The PDFs are unchanged by metadata finalization and need no new editorial revision suffix.

Word originals, earlier manuscripts and internal QA PDFs remain outside the release. They are not extra release papers. The [relocation index](../../release/provenance/RELOCATION_INDEX_20260906.json) and [finalization record](V2_STANDARDS_PDF_FINALIZATION_20260906.md) identify the relevant external editorial records without rewriting their historical bytes.

## Final Documentation Pass

The owner-authorized post-audit revision on 6 September 2026 aligns the current [notice](../../NOTICE.md) and [third-party notice](../../THIRD_PARTY_NOTICES.md) with the v2.0 Standards Edition. It corrects the populated [validation-evidence](../../evidence/v2_validation/README.md) and [private-baseline](../../release/private_baseline/README.md) folder descriptions and clarifies [historical link scope](../../release/provenance/README.md#historical-link-scope). It does not adopt Licence 1.1, grant additional rights, record actual lawyer review or change either PDF, executable control or historical result.

The earlier audited archive `q-pathformer_v2-standards_release_20260906_104118_358Z.zip`, SHA-256 `bbbb8b0c4f7c2be1c7661eb1f2ac00aa5423c64b74cecaad24226c8389e3e81f`, identifies the preceding documentation snapshot, not this revised selection. Use a new timestamped owner seal for the revised folder; do not reuse that archive digest or overwrite historical inventories. The earlier archive was no longer at its recorded location during this revision; the preserved, hash-verified audit manifest supplied the source comparison. No old archive was recreated or modified.

Pre-edit copies, the full before/after comparison and fresh verification records for this documentation pass are retained outside the release under owner-local archive identifier `standards_final_docs_revision_20260906_110154`. The prior audit remains a record of the preceding snapshot. These records do not assert a completed GitHub publication or file-specific rights clearance.

## Owner Completion Order

1. Keep the registered PDFs unchanged. Conversion and visual review are complete; do not re-export them or return Word files to the release merely for packaging.
2. Run the [final-paper check](../execution/LOCAL_CHECKS.md) against the exact selected folder. Confirm both PDFs are registered and hash-matched. Retain new test observations separately from the papers' historical results.
3. Review the exact source selection, inherited licences/notices, applicable distribution permissions and any sensitive historical locators. The fictional legal-review example is not actual clearance.
4. Once the selected contents are final, create the owner's file inventory and checksums, with a documented checksum-file self-exclusion rule. Do not replace historical inventories.
5. Create the final ZIP outside the project folder, then calculate its SHA-256 as an external sidecar. Verify the archive members against the final inventory. If the owner's sealing tool already performs these steps, use that process without duplicating it. Any later content edit requires renewed inventory/seal verification.
6. Separately create/select the GitHub repository and commit, bind the assigned tag to that commit, attach the chosen assets and verify the published links and hashes. A matching archive hash identifies bytes; it does not itself authenticate a signer or grant publication rights.

These are completion instructions, not new release gates or authorization to execute Git/publication actions. No such actions were performed here.

## Preserved Boundaries

The [cleanup record](V2_STANDARDS_CLEANUP_20260906.md) describes earlier folder preparation and limited checker changes. The [finalization record](V2_STANDARDS_PDF_FINALIZATION_20260906.md) locates the external editorial records and documents final PDF registration. Neither changes measured historical results, operative licences, legal review status or actual operational permissions. V3 remains planned and separate.
