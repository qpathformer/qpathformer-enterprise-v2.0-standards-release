# Standards Local Evidence

This directory records the bounded local standards slice of 2026-09-05, not an official release seal or legal approval.

- `unit_tests.txt` records the actual local unittest run, including the environment skip.
- `rehearsal.json` records nine expected CLI outcomes, commands, disposable fixture identities, source hashes and pre-tamper package hashes.
- `workspace_verification.json` records read-only repository-policy, syntax, schema and historical-copy checks.
- `environment.json` records Python/platform versions, the eight matching validation dependency pins and commands.
- `source_inventory.json` identifies the selected code, tests, documentation and preserved history on top of parent HEAD `57c7fbbed476a8f74ba4ca7b6acb495791ba5524`. It excludes this current evidence directory to avoid self-reference. It is an unsigned source identity, not authority or an official frozen-tree seal.

The rehearsal creates synthetic starting STATE_1/registry fixtures; it is not a complete three-path replay or real promotion approval. Keys and temporary packages are removed. No model framework is loaded, no network inference is requested and no training or CSC scoring is reported.

See the [preparation record](../../../docs/release/TR010_STANDARDS_LOCAL_PREPARATION_20260905.md) and [runbook](../../../docs/execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md). These reports qualify the selected local bytes; they do not update historical v1/M11 evidence.
