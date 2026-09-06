# Path 3 External Bundle Commands

Run from the checked-out repository root. This file describes the optional
bring-your-own-bundle route; it is not a claim that an external freeze bundle
is populated in the public candidate.

## Release Boundary

The historical `QPDS-PACKAGE-001` bundle is not included as positive v2
evidence. M03 established that the immutable v1 files are byte-identical to the
retained source but fail their checked-in `hashes.txt`. The bundle and its
normalized output were therefore excluded rather than rewritten or relabelled.

The controlling records are:

- `planning/migration/V1_PATH3_PROVENANCE_RECONCILIATION.json`
- `planning/migration/V2_PUBLICATION_DECISIONS.md`
- `release/EXCLUSIONS.json`

Do not run the commands in this file against `QPDS-PACKAGE-001`, recreate that
bundle from historical fragments, or describe it as validated positive v2
evidence. The populated release test is the client-JSON route in
`docs/execution/path_3_client_custom_dataset_commands.md`.

## Optional Reviewer-Supplied Input

Use this route only when a reviewer supplies a separate governed bundle that
contains the expected `id3_freeze_bundle` members and its own hash manifest.
Replace `<PACKAGE_ID>` below with that folder name.

```powershell
$RepoRoot = (Resolve-Path .).Path
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot 'scripts'))) {
  throw 'Run these commands from the repository root.'
}

$PackageId = '<PACKAGE_ID>'
$ExternalBundle = Join-Path $RepoRoot "path_3_external_custom_adapter\01_source\inbound\$PackageId"
$OutputRoot = Join-Path $RepoRoot 'path_3_external_custom_adapter\03_dataset\normalized'
$RejectedRoot = Join-Path $RepoRoot 'path_3_external_custom_adapter\03_dataset\rejected'

if (-not (Test-Path -LiteralPath $ExternalBundle -PathType Container)) {
  throw "Reviewer-supplied bundle not found: $ExternalBundle"
}
```

The expected bundle shape is:

- `hashes.txt`
- `ID3_FREEZE_NOTE.md`
- `module_03_baseline.canonical.json`
- `module_03_variant.canonical.json`
- `session_baseline.canonical.json`
- `session_variant.canonical.json`

## 1. Strict Dry-Run

```powershell
py -3 .\scripts\run_external_adapter_ingestion.py `
  --input-root $ExternalBundle `
  --output-root $OutputRoot `
  --template-family id3_freeze_bundle `
  --profile-path .\shared\configs\adapter_profiles\id3_freeze_bundle.profile.json `
  --strict-hash-check `
  --write-rejected `
  --rejected-root $RejectedRoot `
  --dry-run
```

Continue only when the command returns `status = ok` and
`hash_verification_status = ok`. A warning or mismatch is a stop condition, not
positive evidence.

## 2. Write Contained STATE_3 Output

```powershell
py -3 .\scripts\run_external_adapter_ingestion.py `
  --input-root $ExternalBundle `
  --output-root $OutputRoot `
  --template-family id3_freeze_bundle `
  --profile-path .\shared\configs\adapter_profiles\id3_freeze_bundle.profile.json `
  --strict-hash-check `
  --write-rejected `
  --rejected-root $RejectedRoot
```

Review the generated package under:

```text
path_3_external_custom_adapter/03_dataset/normalized/<PACKAGE_ID>/
```

Expected records are `onboarding_manifest.json`,
`normalized_onboarding.jsonl`, `source_inventory.json`,
`normalization_report.json`, and `hash_verification_report.json`.

## Interpretation

Successful intake creates a contained `STATE_3` onboarding package. It does
not grant training authorization, promote the input to `STATE_1`, or convert a
reviewer-supplied bundle into release evidence. Any decision to retain a new
result requires a separate provenance and release-scope review.
