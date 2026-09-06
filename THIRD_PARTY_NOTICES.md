# Third-Party Notices for the v2.0 Standards Edition

The root LICENSE and QPATHFORMER-PLATFORM-1.0.txt are retained from the corrected
candidate for this standards selection. This notice does not change their
terms, create a new licence grant or establish redistribution clearance.

## Access-PoD v1a

The retained text/schema/catalogue/profile/example subset is under
`shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/` with its
original MIT LICENSE, README, ORIGIN and manifest. PDFs were not imported.
The original manifest and ORIGIN describe the historical full pack, not this
subset. See `release/provenance/STANDARDS_SUBSET.json` for physical hashes,
manifest-entry coverage and the explicitly allowed CRLF-to-LF comparison.
Files are copied without modifying their physical bytes.

The enterprise bridge schemas, profiles and mapper code remain separate from
the vendored upstream material. No generated certificates or scoring evidence
have been imported or relabelled as current v2 results.

## Models and Dependencies

Only Q-Pathformer reference Python source is included. TinyLlama and gpt-oss
identifiers in inherited code are references, not bundled models or a current
redistribution decision. No weights, adapters, tokenizer downloads or Ollama
cache are included. Model-use and derivative-asset rights remain separate.

`requirements-release.txt` preserves the exact inherited validation dependency
pins. Dependencies are not vendored; their own licences remain applicable.
Optional training and GPU dependencies are not installed by the local checks.

The historical candidate's complete third-party notice is preserved verbatim at
`release/provenance/historical_candidate/release/THIRD_PARTY_NOTICES.md` for
provenance. Its inventory-wide statements refer to that candidate, not this
smaller selection. Recheck current file and dependency treatment before upload.

The current edition wording does not adopt the Licence 1.1 review proposals,
replace nested attribution or represent actual lawyer review. See NOTICE.md
for the owner distribution responsibility and the distinction between file
identity, technical verification and authority.
