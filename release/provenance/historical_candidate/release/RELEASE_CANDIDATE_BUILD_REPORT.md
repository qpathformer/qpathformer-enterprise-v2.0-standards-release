# Q-Pathformer Enterprise v2 Release-Candidate Build Report

## Outcome

Gate M11 completed with status `READY_FOR_HUMAN_RELEASE_REVIEW`. The
candidate was finalized from the M10 pre-seal PASS state and frozen before
the publication inventory, this report, and the checksum file were generated
in the required non-circular order.

## Immutable Source Anchor

- Commit: `cf9721afb81273d82667dd7b33ee5e5f3ad806d9`
- Annotated tag: `v2.0-qpathformer-enterprise-source-baseline`
- Git tree: `866cb4246d4fdc5e31c3a8be32249dc1b00b60ec`

## Frozen Inventory

- Inventory: `release/PUBLICATION_INVENTORY.json`
- Inventory SHA-256: `bed0957ddb1de0b3ed1b76c295f7febc12f7ca53880d7c1fd408996c2bcc07e6`
- Listed regular files: `348`
- Listed bytes: `35619880`
- Canonical listed-file digest: `59ca99c9869cbd26d537a577b7d1f79f487cc999f39408e52c4fa07674f8915d`
- Expected checksum entries after finalization: `350`

The inventory excludes itself, this report, and `release/SHA256SUMS.txt`.
The checksum file is generated last and covers every final regular public
file except itself, including the inventory and this report.

## Pre-Seal Evidence

- M10 report SHA-256: `e1681d941e1ce03eef2def0038286a07caa8d49e2a7863ab2fe940b9ba48a218`
- M10 external gate report SHA-256: `4252fa6ee78f8aaa295e29afb61304567d07b3eca631a17d89682b0de5877741`
- Documentation conformance: `23/23 PASS`
- Unit suite: `24 run; 23 passed; 1 environment-guarded symlink skip`
- JSON Schemas: `27 valid`
- Reviewer CLI entry points: `19 resolved`
- Dependency lock: `8 exact pins; pip check PASS`

Historical v1 CSC records, Path 2 provenance, Path 3 exclusion treatment,
and the Access-PoD vendor pack remain qualified evidence. They are not
recast as current v2 certification, model-quality proof, or retroactive
governance claims.

## M11 Boundary

M11 performed candidate finalization, inventory generation, checksum binding,
and read-only digest reproduction. It did not initialize Git, create a public
commit or tag, create a ZIP asset, push content, or publish APOD-TR-010.
Those actions remain subject to later explicit authorization and external
human release review.
