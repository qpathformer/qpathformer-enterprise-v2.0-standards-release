# Download Optional Models

The model identifiers below are historical v1.0 execution references. Models
are not included in the v2 repository and are not required for release
validation, documentation review, or unit tests.

This note records which model identifiers were used in the release, where they
come from, and the safest ways to download the same models for reviewer or test
runs.

## Release Models Used

### Runtime signal model

- Release model id: `gpt-oss:20b`
- Used for: Path 2 runtime-signal route
- Runtime host: local Ollama server
- Release command location:
  `docs\execution\path_2_access_mode_canonical_runtime_signal_commands.md`

Official references:

- Ollama model page: <https://ollama.com/library/gpt-oss:20b>
- Ollama library page: <https://ollama.com/library/gpt-oss>
- Ollama download page: <https://ollama.com/download>

PowerShell 7 example:

```powershell
ollama pull gpt-oss:20b
ollama list
ollama run gpt-oss:20b
```

Historical runtime note:

- the runtime route in this repository uses the exact tag `gpt-oss:20b`
- if you write `gpt-oos-20B`, treat that as a typo; the live release tag is
  `gpt-oss:20b`
- Ollama normally resolves its own model store; use `OLLAMA_MODELS` when a
  non-default model directory is configured

Local verification example:

```powershell
$OllamaModels = if ($env:OLLAMA_MODELS) {
  $env:OLLAMA_MODELS
} else {
  Join-Path $HOME '.ollama\models'
}
Get-ChildItem -LiteralPath $OllamaModels -Force
```

### Local LoRA base model

- Release model id: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- Used for: Path 1 and Path 2 local LoRA validation runs
- Active backend profile:
  `shared\configs\training_backend_profile.local_lora.json`

Official references:

- Hugging Face model page:
  <https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0>
- Hugging Face CLI guide:
  <https://huggingface.co/docs/huggingface_hub/guides/cli>
- Hugging Face CLI reference for `hf download`:
  <https://huggingface.co/docs/huggingface_hub/package_reference/cli>

PowerShell 7 example:

```powershell
# Install the `hf` CLI by following the official guide linked above, then run:
hf download TinyLlama/TinyLlama-1.1B-Chat-v1.0 `
  --local-dir .\models\TinyLlama-1.1B-Chat-v1.0
```

Historical local LoRA note:

- the active local LoRA backend profile points to the Hugging Face repo id
  `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- if the model is not already cached locally, the finetune flow can also fetch
  it through the normal Transformers/Hugging Face path during runtime

## Use Different Models

### Change the Path 2 runtime model

Edit only the model tag used in the runtime command.

Current release example:

```powershell
py -3 .\scripts\runtime\run_runtime_signal_emitter.py `
  --prompt "Summarize runtime governance signals for the current Access-Mode session." `
  --model gpt-oss:20b `
  --session-id $Path2RuntimeSessionId `
  --signal-root $Path2RuntimeSignalRoot
```

Controlled alternatives:

- another Ollama-served `gpt-oss` tag such as `gpt-oss:120b`
- another local Ollama model tag that your runtime route is intentionally being
  tested against

Keep in mind:

- changing `--model` changes the runtime route only
- it does not change Path 1 or Path 2 local LoRA validation
- use a new session id when you want a clean runtime package lineage

### Change the local LoRA base model

Do not patch `run_state1_finetune_local_lora.py` just to swap models.

The supported release-safe path is:

1. Update `model.model_base` in
   `shared\configs\training_backend_profile.local_lora.json`.
2. Rebuild the training package so the generated
   `training_backend_profile.json` carries the new model base.
3. Run the usual `run_state1_finetune_local_lora.py` flow against that rebuilt
   package.

Current release default:

```json
"model": {
  "model_base": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
  "model_family": "llama"
}
```

Compatibility note:

- the easiest substitutions are small causal LM checkpoints that stay compatible
  with the current local LoRA profile
- if you switch model families, review the LoRA target modules and backend
  profile before treating the run as comparable to the release default

## Practical Reviewer Notes

- model licences and usage terms remain separate from the Q-Pathformer
  platform licence
- this repository does not redistribute base weights, tokenizer files, LoRA
  adapters, checkpoints, or optimizer state
- use the release defaults first before trying alternates
- Path 2 runtime tests expect `gpt-oss:20b`
- Path 1 and Path 2 local LoRA validation expect the backend profile model base
  to stay aligned with the training package
- CLI overrides such as `--max-steps`, `--learning-rate`, and `--batch-size`
  change run settings only; they do not change the base model
