# Private Development Baseline

Date: 2026-09-05. Repository: `qpathformer/qpathformer-enterprise-v2`.
Classification: **Private development source baseline, not an official release.**

## Scope and Identity

The user requested the initial private development baseline after local
preparation and asked that provenance be retained locally and prepared for Git.
The repository was created as private, non-fork, ID `1357710753`. The signed-in
account was an organization administrator. At the pre-upload access check the
organization listed one member, `Ante-PoDs`, and no teams. Base permission was
`read`; future organization members could inherit access.

The initial baseline retains 170 unchanged inherited files, including historical
records and the standards subset. The 562,752-byte TR010 working draft is copied
without changing its original bytes, under a clearly marked working-draft name.
Its SHA-256 is `44295dbe0cad76a6c4fc0edfe52a760070796d3f8c14d18cb63909fc4cf7883d`.
The original source, candidate, records and manuscript remain unchanged.

## Changes Since Local Preparation

The document allowlist and Git ignore rule admit only that exact TR010 path.
The private-workspace validator checks its hash/size, rejects macro/embedded
binary content, and scans document XML text without extraction or modification.
New synthetic tests cover identity mismatch, path restrictions, traversal,
duplicates, and macro/embedded-content rejection. No lifecycle or training
authorization implementation has been changed.

Current scope/index documents distinguish this private baseline from the earlier
local-only preparation record. Initial provenance catalogues remain preserved;
the additive exception and baseline delta explain the changed selection.
Licence 1.1 is not adopted. Other papers, derived datasets, raw run folders,
weights, credentials and persistent private keys remain excluded.

Before the initial commit, the user also supplied the July 21 TR010 document
seal. Its ZIP hash matches both supplied archive records; all five content-file
hashes/sizes and the embedded manifest match the original sidecars. The original
manifests and checksum, plus the measured verification report, are retained in
[historical seal provenance](../../release/provenance/historical_seals/tr010_docs_20260721_100018/README.md).
The ZIP remains external. Neither sealed manuscript matches the selected
private draft's hash. This distinct historical identity does not seal the
current manuscript or repository and does not change the selected draft.

## Verification and Follow-Up

Local baseline check results, test logs and environment metadata are retained
under `release/private_baseline/`. GitHub CI results apply to the actual pushed
commit and must be checked after upload, not inferred from this document.
This pre-commit record does not invent its own commit hash or a future CI result.

Single-scope authorization, endpoint binding, and the isolated v2 execution
runbook remain the next application-development slice. Historical M12/M13
records do not approve the new repository. No M00 restart, public visibility
change, tag, GitHub Release, ZIP asset, new CSC result or model training is
authorized by this private-baseline action.

A future official release will be a separate reviewed public export. Internal
history, earlier drafts and private development releases need not become public.
