# Three-Path Quick Prompts

Use these prompts from the root of the checked-out repository. New executions
create local test evidence; they do not replace the qualified historical
release records without a separate review decision.

## Preflight Prompt

```text
Use the current checked-out repository root. Read the relevant execution doc in docs\execution, confirm Python is available with py -3, and then run only the requested path end to end. After each step, report what was created, which key files to inspect, and whether the path is ready for the next stage.
```

## Path 1 Prompt

```text
Run Path 1 end to end from the repository root using docs\execution\path_1_tr_corpus_reference_commands.md as the source of truth. Execute the TR corpus flow in order: corpus snapshot, TR signals, strict fine-tune dataset, STATE_1 package, and local LoRA training dry-run first, then a one-step smoke run only if the package outputs are valid. After each step, check the files listed in the command doc and summarize the created outputs under path_1_tr_corpus_reference\01_source, 02_signals, 03_dataset, 04_state1_package, and 05_runs.
```

## Path 2 Source-First Prompt

```text
Run the release-default Path 2 source-first route from the repository root using docs\execution\path_2_access_mode_canonical_source_first_commands.md as the source of truth. Execute the Access-Mode canonical lifecycle in order: source verification, source bridge signal build, candidate export, STATE_2 review, STATE_2 promotion decision, STATE_1 handoff, STATE_1 freeze, registry update, training package build, and local LoRA dry-run first, then a one-step smoke run only if the package outputs are valid. After each step, report the created files and confirm the lifecycle state reached.
```

## Path 2 Runtime Prompt

```text
Run the Path 2 runtime-only route from the repository root using docs\execution\path_2_access_mode_canonical_runtime_signal_commands.md as the source of truth. Emit the runtime signal with gpt-oss:20b if available, export candidates from the runtime signal root, and continue only as far as the package satisfies the documented promotion gates. After each step, report the created files and whether the path remains in STATE_3, advances through STATE_2, or is promoted into STATE_1.
```

## Path 3 External Prompt

```text
Read docs\execution\path_3_external_custom_adapter_commands.md and confirm that a reviewer-supplied external bundle is present. Do not use or recreate the excluded historical QPDS-PACKAGE-001 bundle as positive v2 evidence. If a separate bundle has been supplied, run strict hash validation in dry-run mode first and continue to live STATE_3 normalization only when that check passes. Otherwise stop and report that the optional external-bundle test is not applicable to the populated release tree.
```

## Path 3 Client Prompt

```text
Run the Path 3 client JSON branch from the repository root using docs\execution\path_3_client_custom_dataset_commands.md as the source of truth. First run the client adapter intake in dry-run mode, then run the live normalization intake. Report whether the client JSON is accepted into normalized STATE_3 onboarding or written to rejected output.
```

## Full Three-Path Prompt

```text
Run a staged validation pass for the populated Q-Pathformer historical release paths from the repository root. Use the docs in docs\execution as the source of truth. Complete Path 1 first, then Path 2 source-first, then the populated Path 3 client-JSON route. For each path, execute the documented steps in order, stop on validation failure, and summarize: 1) commands run, 2) files created, 3) key manifests reviewed, 4) lifecycle state reached, and 5) blockers before the next path or next stage. Treat the optional external-bundle route as not applicable unless a reviewer supplies a separate bundle.
```
