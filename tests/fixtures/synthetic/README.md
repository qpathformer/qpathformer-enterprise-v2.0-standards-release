# Synthetic Fixtures

The inherited unit tests construct their own synthetic rows, packages, registries
and disposable signing keys inside temporary directories. No historical TR
papers, corpus, client data or model weights are needed to run them.

Do not copy the old untracked `tests/fixtures` directory here. Any new checked-in
fixture must have an explicit synthetic origin and must not contain live keys.
