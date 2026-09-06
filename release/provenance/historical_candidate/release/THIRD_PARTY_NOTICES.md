# Third-Party Notices

## Scope

Q-Pathformer Enterprise source is provided under
`QPATHFORMER-PLATFORM-1.0`; see the repository-root `LICENSE` and
`QPATHFORMER-PLATFORM-1.0.txt`. That licence does not replace the separate
licences and usage terms below and does not grant model redistribution rights.

## Access-PoD V1a Material

The vendored Access-PoD subtree at
`shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/` retains its
MIT `LICENSE`, `README.md`, `ORIGIN.md`, and original
`manifest_v1a_pack.json`.

The nested MIT licence and two other files verify byte-for-byte. Six retained
files use CRLF rather than LF line endings. Applying only the documented
CRLF-to-LF transform reproduces each original manifest byte count and SHA-256
exactly. Physical and canonical identities are both pinned in
`release/V1_STANDARDS_VENDOR_VERIFICATION.json`; no broader content
normalization or upstream byte-exactness claim is made for the physical CRLF
copies.

Upstream reference:
<https://github.com/Access-PoD/access-pod-artifacts-core/releases/tag/v1a>

## Referenced Models

### gpt-oss:20b

Historical Path 2 runtime records reference the Ollama model identifier
`gpt-oss:20b`. The model is separately obtained and is subject to Apache-2.0
and applicable gpt-oss usage terms. No model weights or Ollama cache files are
included.

References:

- <https://openai.com/index/gpt-oss-model-card/>
- <https://ollama.com/library/gpt-oss:20b>

### TinyLlama/TinyLlama-1.1B-Chat-v1.0

Historical Path 1 and Path 2 local LoRA continuity records reference
`TinyLlama/TinyLlama-1.1B-Chat-v1.0`, distributed separately under
Apache-2.0. No base weights, tokenizer bundle, LoRA adapter, checkpoint, or
optimizer state is included.

Reference:
<https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0>

## Release-Validation Dependencies

The exact release-validation dependency set is in
`requirements-release.txt`. These packages are installed by CI but are not
vendored into the repository.

| Package | Version | Licence expression |
| --- | --- | --- |
| attrs | 26.1.0 | MIT |
| cffi | 2.1.0 | MIT-0 |
| cryptography | 49.0.0 | Apache-2.0 OR BSD-3-Clause |
| jsonschema | 4.26.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| pycparser | 3.0 | BSD-3-Clause |
| referencing | 0.37.0 | MIT |
| rpds-py | 0.30.0 | MIT |

Optional runtime, model, training, and GPU dependencies are not part of the
release-validation lock or clean-checkout CI path.
