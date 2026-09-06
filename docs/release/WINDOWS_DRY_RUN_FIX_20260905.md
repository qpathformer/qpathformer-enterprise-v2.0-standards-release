# Windows Dry-Run Test Investigation

Slice: `WINDOWS-DRYRUN-001`. Date: 2026-09-05.
Status: **Reproduced and fixed locally; hosted-CI confirmation pending.**
Parent baseline: `52c56d34e248e43ea1fe3d1208507d0f3e365f85`.

## Finding

The initial [GitHub Actions run](https://github.com/qpathformer/qpathformer-enterprise-v2/actions/runs/33935542960)
passed on Ubuntu but failed one Windows assertion: the synthetic authorization
and package-seal dry run returned `1` instead of `0`. Both platforms passed
the private file/provenance checks. The original test suppressed the CLI's
error text, so that run did not itself identify the underlying exception.

The same assertion failure was reproduced locally using real Windows 8.3
short-name temporary paths and, independently, an equivalent path containing
`..`. In both cases the captured CLI error was:

```text
unsupported_training_package_path_for_top_level_run_log:<resolved package path>
```

The test installed an unresolved temporary path as `PATH1_ROOT`. The runtime
resolved the package path to its canonical spelling and then performed a
relative-path comparison. The same folder therefore failed the comparison
when the test used a different spelling. The normal application roots in
`scripts/path_layout.py` already derive from a resolved repository root.
This is a test-fixture mismatch, not evidence of a broken signature or an
insufficient authorization. Confirmation on a new hosted run remains pending.

## Narrow Fix

In [the authorization test](../../tests/unit/test_training_authorization_v2.py),
resolve the temporary fixture root before creating paths or patching the
runtime's path root. A shared exercise now runs the original scenario and
two regression cases: `..` spelling and a real Windows short-name alias.
The new cases failed before the fix and passed after it. The Windows-specific
case reports a skip where that operating-system feature is unavailable;
the `..` regression is cross-platform and does not rely on that feature.

Failed assertions now include the captured CLI result. The successful dry-run
call also has a test guard that fails if real LoRA training is entered. Each
scenario still verifies authorization/seal evidence, tampers with the dataset,
and asserts rejection with no rejected-run output directory.

Production code, authorization semantics, seal validation, model settings,
dependency pins, CI workflow, TR010 manuscript and historical records were
not changed. F01 single-scope, F02 endpoint binding and F03 runbooks remain open.

## Verification

Local Windows results: **33 tests run, 32 passed, one skipped**. The unrelated
export-symlink test skipped because local symlink creation is unavailable.
The real short-name regression did run and pass. All three diagnostic path
forms returned `0` for valid dry runs and `1` for tampered packages, with
`package_inventory_verification_failed` for the latter.

From the private repository root in PowerShell 7:

```powershell
py -3 -B -m unittest discover -s .\tests\unit -p 'test_training_authorization_v2.py' -v
py -3 -B -m unittest discover -s .\tests\unit -p 'test_*.py' -v
py -3 -B .\tools\verify_private_workspace.py
git -c core.whitespace=cr-at-eol diff --check
```

The normal workspace check passes and lists the intentionally changed test.
`--verify-origin-bytes` is an original-copy identity check, not the development
acceptance check: it is expected to fail for this one changed test. Do not
rewrite its recorded origin hash to hide that change.

See the [slice provenance record](../../release/provenance/development_slices/WINDOWS_DRY_RUN_FIX_20260905.json)
and [local test log](../../evidence/v2_validation/windows_dryrun_20260905_unit_tests.txt).
The local investigation performed no commit, push, tag, release or training run.
The user's subsequent instruction authorizes a focused branch commit/private
push, PR and fresh GitHub CI run. The persisted slice record is a pre-commit
snapshot; use checks on the actual PR commit for hosted results. The failed
baseline run remains historical evidence, not a result to relabel as PASS.

## Follow-Up Development

These are specific errors and test gaps, not new release phases or changes
included in this test-fixture fix. Record them on the PR and keep it unmerged
until reviewed.

- **Observed error:** an unsupported training-package/log-routing path returns an error but leaves an empty run directory. An isolated synthetic check confirmed this; `run_dir.mkdir(...)` occurs before `_resolve_run_log_profile(...)`. Validate routing before output creation and add a no-side-effects regression in a separate focused change.
- **Authorization coverage:** add signed DENY, expiry/not-before boundary, dataset version/hash/registry mismatch, and reused-key negative tests. Assert no output or trainer entry on rejection. Existing signature-tampering and wrong-key tests should remain.
- **Open contract gaps:** the single-scope rule and endpoint-to-operation binding still need implementation with multi-scope and wrong-operation negative tests. Passing this PR does not resolve those behavior gaps.
- **Error visibility:** carry captured CLI errors into other assertions that currently discard stdout, while keeping synthetic key material out of logs. Distinguish unsupported-feature skips from executed regression coverage.
