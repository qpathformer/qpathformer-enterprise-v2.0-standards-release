# Local Standards Consolidation Provenance

This is unsigned local preparation evidence, not an official release seal or legal approval.

`SOURCE_CAPTURE.json` identifies all 271 selected source files captured from the private development working tree, including its uncommitted changes. Parent HEAD is `57c7fbbed476a8f74ba4ca7b6acb495791ba5524`; the parent commit alone does not identify that working tree. `.git`, `.local`, `.venv`, bytecode and caches were not copied.

`FINAL_LOCAL_INVENTORY.json` identifies the final selected files after the documentation/example/manuscript consolidation. Its only excluded file is itself, avoiding recursive hashing. It records each path, byte count and SHA-256; these checks provide byte identity, not ownership, permission or an approved release state.

`CONSOLIDATION_DELTA.json` identifies additions and changed files against the captured source. Application code, tests already present, dependency pins, `shared/standards`, operative licence texts, earlier paper bytes and historical evidence remain unchanged. New illustrative fixture files are documentation data, not reviewed client material or runtime approvals.

The final inventory is a point-in-time local record. Later edits require a new record and review; do not silently rewrite earlier provenance to hide them. The original private repository is retained separately and is not modified by this consolidation.
