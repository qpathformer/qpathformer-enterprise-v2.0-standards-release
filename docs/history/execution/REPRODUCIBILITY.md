# Reproducibility And Clean-Checkout Validation

## Review First

The repository is pre-populated with historical path outputs. Reviewers do not
need to execute a path, download a model, or use GPU hardware to inspect the
release candidate.

## Release Validation Environment

Required:

- Python 3.11;
- dependencies pinned in `requirements-release.txt`;
- a checkout of the selected repository tree.

Not required:

- Ollama or `gpt-oss:20b`;
- TinyLlama or any Hugging Face model download;
- CUDA, GPU hardware, or optional training libraries;
- private data, private keys, local registries, or machine-specific paths.

## Clean-Checkout Commands

Open PowerShell 7 in the repository root and run:

```powershell
$RepoRoot = (Resolve-Path .).Path
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot 'scripts'))) {
  throw 'Run these commands from the repository root.'
}

py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r .\requirements-release.txt
.\.venv\Scripts\python.exe .\scripts\validate_v2_release.py --root . --check-only
.\.venv\Scripts\python.exe -m unittest discover -s .\tests\unit -p "test_*.py" -v
```

The CI workflow performs the same release validator and unit-test suite on a
clean checkout.

## Path Execution

Path execution is optional and can create new local artifacts. Use one command
guide at a time:

- Path 1: `path_1_tr_corpus_reference_commands.md`.
- Path 2 source-first: `path_2_access_mode_canonical_source_first_commands.md`.
- Path 2 runtime-only: `path_2_access_mode_canonical_runtime_signal_commands.md`.
- Path 3: `path_3_external_custom_adapter_commands.md`.

Run each guide from the repository root. Do not treat a new local run as a
release result until it receives a separate evidence review and release
decision.

## Expected Boundaries

- Unit and release validation prove included controls and repository
  conformance within their tested scope.
- Historical fine-tune completion proves execution continuity, not model
  quality.
- Historical CSC values remain qualified v1.0 evidence, not v2 scores.
- A lifecycle hold is a valid fail-closed outcome, not an execution failure.
