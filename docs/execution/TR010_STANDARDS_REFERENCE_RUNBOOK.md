# TR010 Standards Reference Runbook

Date: 2026-09-05. Scope: local synthetic research rehearsal, not a public release or legal approval.

## Start Here

Use the consolidated local standards workspace, not a v1 release directory. This runbook exercises the `qpath_training_authorization_v2.2` single-scope contract. It does not read the historical `01_source` examples, download models, call Ollama, train TinyLlama, or generate a CSC score.

Use PowerShell 7 and Python 3.11 with the lightweight packages in `requirements-release.txt`. If they are missing, inspect that file and install its pinned dependencies in an isolated environment following [local checks](LOCAL_CHECKS.md). No new dependency or installer is required by this slice.

```powershell
Set-Location 'C:\q-pathformer_v2-standards_release'
py -3.11 -B .\tools\verify_private_workspace.py
if ($LASTEXITCODE -ne 0) { throw 'Workspace verification failed.' }

py -3.11 -B -m unittest discover -s .\tests\unit -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Unit checks failed.' }

$Report = Join-Path (Get-Location) ('.local\standards-review\rehearsal-' + [guid]::NewGuid().ToString('N') + '.json')
py -3.11 -B .\tools\rehearse_standards_release.py --report $Report
if ($LASTEXITCODE -ne 0) { throw 'Synthetic rehearsal failed; inspect the report.' }
Get-Content -Raw -LiteralPath $Report
```

The report path must be new. The tool refuses to replace an existing report. Retain the generated report as evidence; its random fixture identifiers and signatures are intentionally different on another run. Compare the outcome contract and source hashes, not random IDs or elapsed time.

The [illustrative legal-review record](../legal-review/ILLUSTRATIVE_LEGAL_REVIEW_WORKED_EXAMPLE.md) is separate documentation. It remains on actual HOLD and is not used to authorize this rehearsal. No command in this runbook converts that fictional review into real approval.

## What Runs

The source-preparation check above can pass while the two owner-exported PDFs remain pending. Before sealing, complete the separate `--require-final-papers` check in [local checks](LOCAL_CHECKS.md). This does not change the synthetic execution flow or add a release milestone.

The harness copies an explicit script allowlist into a temporary repository-shaped workspace. Child processes invoke the real CLIs with explicit paths. A test-only bootstrap rejects model-framework imports, socket connections and non-dry-run fine-tuning. It is a rehearsal safety measure, not a production sandbox claim.

The starting registry and STATE_1 freeze are four-record synthetic fixtures. They do not represent actual legal review, human promotion or replay of the complete Path 1, Path 2 or Path 3 lifecycle.

| Step | Expected result |
|---|---|
| Generate the synthetic authorization key | Success; disposable test key only. |
| Generate a distinct package-sealing key | Success; separate cryptographic role. |
| Create one explicit synthetic ALLOW scope | Success for `validation_parameter_update`. |
| Attempt multiple scopes | Rejection; no authorization output. |
| Prepare the research training package | Success; signed authorization and separate package seal. |
| Run the local trainer in dry-run mode | Success artifacts explicitly record `dry_run: true`; no model is loaded. |
| Request `model_release` at the research endpoint | Rejection before success output. |
| Use an unsupported package/log route | Rejection; no final run directory. |
| Tamper with the sealed training data | Rejection; no final run directory. |

The report records nine outcomes, commands, source hashes, package hashes before deliberate tampering, valid dry-run artifact hashes and checks that synthetic source/registry bytes did not change. Temporary keys and workspaces are removed. The report is not a persistent reusable authorization package.

## Contract and Migration

ALLOW requires exactly one explicit supported scope; DENY requires an empty list. Zero, repeated, multiple, unknown and whitespace-altered scope identifiers are rejected. There is no implicit default in the authorization creator. A signature on DENY authenticates a denial, not permission.

The preparation, migration and local LoRA endpoints accept only `validation_parameter_update`. Their existing `--authorization-scope` option is a compatibility assertion, not a switch that turns the endpoint into production training, external-provider training, model release or deployment. Other names remain in the general vocabulary but those operations are not implemented here.

All v2.1 authorization artifacts are rejected by this contract, including previously single-scope artifacts. Preserve them unchanged as historical evidence. A fresh explicit human decision must produce a newly signed v2.2 artifact; use the existing copy-based migration tool with that artifact and a separately trusted sealing key to create a new package. Never edit a signed JSON file, reuse an old signature or overwrite a historical sealed package to upgrade it.

One scope is not one use. This slice does not implement consumption, revocation infrastructure, replay prevention, professional-credential verification or automatic evaluation of free-text legal conditions.

## Human Review Boundary

Synthetic local testing can precede retaining counsel. Before rights-dependent use beyond that testing, the proposed standards profile requires a qualified legal practitioner to review the identified materials, intended activity, relevant jurisdictions, permissions and unresolved exceptions. The responsible organization must separately authorize the named operation. This is a project policy, not a claim that every AI experiment is legally required to retain a lawyer.

AI may assist inventory and drafting; its output is not accepted as the required practitioner review or organizational approval. The current code verifies recorded technical bindings, not the existence or adequacy of that legal review. No lawyer review is recorded for this candidate. See the [local preparation record](../release/TR010_STANDARDS_LOCAL_PREPARATION_20260905.md).
