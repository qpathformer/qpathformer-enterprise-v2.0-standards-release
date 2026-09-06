# Local Standards Checks

Use Python 3.11 and PowerShell 7. The lightweight validation dependencies are pinned in `requirements-release.txt`; no Ollama, model weights or GPU packages are needed. Inspect the dependency file before installing it in an isolated environment if needed.

## Source Preparation

From the repository root:

```powershell
py -3.11 -B .\tools\verify_private_workspace.py
if ($LASTEXITCODE -ne 0) { throw 'Workspace verification failed.' }
py -3.11 -B -m unittest discover -s .\tests\unit -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Unit checks failed.' }
```

The checker verifies source selection, immutable historical copies, standards hashes, Python syntax, JSON/schema definitions, limited secret patterns and registered document identities. It does not grant publication permission or validate legal rights.

An empty PDF allowlist is permitted during owner conversion. It reports `final_pdf_pair_registered: false`; this preparation PASS is **not readiness to seal**. Any unregistered PDF or Word file placed in the release fails the file-policy check.

## Final Paper Presence and Identity

The two final PDFs are registered by exact path, byte count and SHA-256 in `release/PAPER_RELEASE_SELECTION.json` and `release/provenance/DOCUMENT_ALLOWLIST.json`. Their 43 and 30 pages were visually reviewed before registration. Keep their bytes unchanged; any later edit or re-export requires renewed review and registration, not merely a hash change to obtain PASS.

```powershell
py -3.11 -B .\tools\verify_private_workspace.py --require-final-papers
if ($LASTEXITCODE -ne 0) { throw 'Final PDF selection is incomplete or does not match its registered bytes.' }
```

This check fails if either registered paper is missing, changed or not selected. PDF checks verify exact bytes plus a basic header/end marker; they do not replace visual review, hyperlink review, compressed-content inspection or a full PDF security audit. Word originals are kept outside the release.

## Origin and Historical Evidence

`--verify-origin-bytes` additionally compares active inherited source with its initial copy hashes. It is a historical-baseline diagnostic, not a requirement that intentional development never change code. Current source differences must remain recorded separately; do not rewrite the origin inventory to obtain PASS.

No Git initialization is needed. Existing historical validators and runbooks under `docs/history/` apply to their original candidates, not this layout.

Unit tests use synthetic fixtures and disposable keys in temporary directories. They do not issue real authorization, train a model or change historical records. A capability-dependent skip remains a skip in that new run. `-B` avoids bytecode caches.

Use the [reference runbook](TR010_STANDARDS_REFERENCE_RUNBOOK.md) for the nine-step synthetic CLI rehearsal. Keep its generated report outside the final release selection unless separately reviewed.
