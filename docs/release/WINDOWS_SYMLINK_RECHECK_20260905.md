# Windows Symbolic Link Test Recheck

Date: 5 September 2026. Scope: one existing test and a separate native filesystem capability probe. This is not a full-suite rerun, a release gate or a change to the release model.

## Result

The targeted retry attempted one test: **zero passed, one skipped, zero failures and zero errors**. The test reported `symlink creation is unavailable`. A separate disposable-file probe returned Windows error **1314**, `A required privilege is not held by the client`. The assertion that the exporter rejects the link was not reached.

The earlier 48-test result remains **47 passed, one skipped, zero failed**. Its log did not preserve the underlying operating-system error code; today's probe does not establish that the earlier skip had the same cause. No earlier log was rewritten, and this retry is not an additional distinct test to add to the original suite count.

The [machine-readable diagnostic](../../evidence/v2_validation/windows_symlink_recheck_20260905/symlink_recheck.json) records the exact test identifier, environment, timestamp, test log, independent capability error and hashes of the unchanged exporter and test source.

## What the Test Protects

The test is `ExportV2PublicReleaseTests.test_source_symlink_is_rejected_when_supported` in [the exporter tests](../../tests/unit/test_export_v2_public_release.py). It creates a real filesystem symbolic link pointing to another disposable file, then expects the [exporter](../../scripts/export_v2_public_release.py) to reject that source path with `reparse_or_symlink_rejected`, even when its target is inside the source folder.

A symbolic link redirects a file path. Rejecting it helps prevent a path on the approved file list from silently selecting different material. This is not an ordinary Windows shortcut (`.lnk`). The test does not claim exhaustive coverage of every reparse-point type or race condition.

## Why Retain the Skip

The skip is a test-coverage limitation, not an exporter failure and not a passing security check. Keeping a short qualification and its evidence lets reviewers distinguish tested behavior from behavior the environment could not exercise. Removing it would make the results appear stronger than they are.

Ordinary source export does not require users to enable symbolic-link creation. Retain the test for environments that can exercise it, and keep the limitation in the results record. It need not be repeated throughout the manuscript. A future passing execution should be added with its own source identity and environment, not substituted into the older log.

## Focused Follow Up

A controlled Windows process with symbolic-link capability can rerun just this test. Python documents that unprivileged symbolic links on Windows depend on Developer Mode; otherwise the process needs the applicable privilege or administrative capability. Any machine-policy or privilege change requires separate approval. [Python 3.11 documentation](https://docs.python.org/3.11/library/os.html#os.symlink)

From the selected repository root, this command invokes the existing test unchanged:

```powershell
py -3 -B -m unittest discover `
  -s .\tests\unit `
  -p test_export_v2_public_release.py `
  -k test_source_symlink_is_rejected_when_supported `
  -v
```

Run it only in the intended test environment: its fixture creates and removes temporary files. A retry with unchanged capabilities may skip again. A completed assertion is required before recording PASS; `OK (skipped=1)` is not PASS for this test.

One bounded test-hardening revision is worth considering: the present fixture catches every `OSError` from link creation. Recognize only expected unsupported-capability or missing-privilege conditions, include the exact error in the skip reason, and let unexpected setup errors fail. A mocked rejection check can supplement but cannot replace the real-link test. No test or product code was revised in this recheck.

The diagnostic did not change Developer Mode, Windows privileges, repository code or historical records. It did not request Windows administrative elevation, perform model training, initialize Git, commit, tag, seal, publish or restart M00-M13.
