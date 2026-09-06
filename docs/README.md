# Documentation - Q-Pathformer Enterprise v2.0

## Purpose

This is the reviewer-facing entry point for the standards pack. It follows the TR008-TR009 separation between architecture, execution and paper/results interpretation without importing v1.0's full enterprise runtime dataset.

## Folder Guide

| Folder | Role | Start here |
|---|---|---|
| `architecture/` | System structure and authority boundaries | [Architecture](architecture/README.md) |
| `execution/` | Current synthetic reproduction, not old enterprise commands | [Runbook](execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md) and [checks](execution/LOCAL_CHECKS.md) |
| `research/` | One TR010 and one TR010-R PDF, with registered identities | [Paper index](research/README.md) |
| `legal-review/` | Fictional example and actual pending-review distinction | [Legal-review index](legal-review/README.md) |
| `release/` | Edition scope, publication handoff and dated preparation records | [Release notes](release/V2_STANDARDS_RELEASE_NOTES.md) |
| `history/` | Byte-preserved legacy commands and July reference material | [Historical boundary](history/README.md) |

The existing research folder has the orientation role used in v1.0. It is not renamed because manuscript identities and current records already reference it.

## Reading Order

1. Read the [two-paper index](research/README.md). Both final PDFs are present and registered; Word files are not release contents.
2. Use the [architecture summary](architecture/README.md) and [repository layout](REPOSITORY_LAYOUT.md) to understand the selected system.
3. Inspect [dated evidence](../evidence/v2_validation/standards_local_20260905/) and the [provenance index](../release/provenance/README.md).
4. For bounded reproduction, follow only the [current runbook](execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md).
5. Before sealing, follow the [owner publication handoff](release/V2_STANDARDS_PUBLICATION_HANDOFF_20260906.md).

## Records and Limits

The [cleanup record](release/V2_STANDARDS_CLEANUP_20260906.md) retains its dated selection and checker-update scope. The [final PDF registration record](release/V2_STANDARDS_PDF_FINALIZATION_20260906.md) identifies the current two PDFs and the externally preserved editorial records. Those earlier records are not extra bundled papers and are not rewritten by this registration.

[Historical consolidation](release/LOCAL_STANDARDS_CONSOLIDATION_20260905.md), [September implementation preparation](release/TR010_STANDARDS_LOCAL_PREPARATION_20260905.md), [Windows dry-run fix](release/WINDOWS_DRY_RUN_FIX_20260905.md) and [symbolic-link recheck](release/WINDOWS_SYMLINK_RECHECK_20260905.md) retain their dated scope. Earlier document paths are resolved through the [relocation index](../release/provenance/RELOCATION_INDEX_20260906.json), not rewritten inside historical evidence.

No new model run, CSC score, actual legal review or publication authority follows from this navigation cleanup.
