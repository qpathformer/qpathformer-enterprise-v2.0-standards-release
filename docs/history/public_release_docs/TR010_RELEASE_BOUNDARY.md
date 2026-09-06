# TR-010 Repository Release Boundary

## Purpose

This document defines what the Q-Pathformer Enterprise v2 repository can
substantiate before the final APOD-TR-010 paper is bound to a public commit,
tag, inventory, and release asset.

## Implemented And Testable

The repository includes testable controls for:

- fail-closed lifecycle transitions;
- explicit, scoped Ed25519 training authorization;
- complete-package member hashing and asymmetric sealing;
- deterministic public-tree export controls;
- three-path dataset and signal handling;
- schema, provenance, documentation, licence, path, secret, and size checks.

These controls substantiate implementation and reproducible behavior within
the included test and example scope.

## Historical Evidence

Populated Path 1, Path 2, Path 3, model-evaluation, and CSC artifacts are v1.0
historical evidence. They are retained for inspection and execution
continuity. They were not regenerated under v2.

Historical fine-tune and evaluation metadata is not model-quality proof.

The selected CSC profiles are Path 2-derived historical evidence:

- Finance: 91.9, Level 5, 16 of 60 catalogue metrics observed.
- Healthcare: 84.6, Level 4, 12 of 60 observed.
- Public: 93.0, Level 5, 12 of 60 observed; curated example.
- AI / emerging technology: 82.9, Level 4, 12 of 60 observed; curated example
  and sector validation not met.

Every presentation of these values must retain coverage, confidence,
provisionality, direct-versus-proxy evidence, and sector-validation
qualifications. The values do not establish certification or general sector
performance.

## Claims Not Made

This repository does not claim:

- a regulatory certification or compliance determination;
- an accredited certification scheme;
- governance, legal, ethical, or release authority for an automated system;
- that lifecycle state alone authorizes training;
- that package sealing approves package content;
- that a historical local LoRA run establishes model quality;
- that sparse historical CSC coverage proves general governance effectiveness;
- that the v1.0 CSC artifacts are recalculated v2 Assurance Records;
- that the repository redistributes any base model or derivative model asset.

`CSC Assurance Record` is the non-certifying v2 working term. Versioned v2
schema and renderer work remains a later implementation slice and does not
alter the retained v1a or v1.0 contracts.

The v2 governance snapshot and scoring design baseline is defined in
[`V2_CSC_GOVERNANCE_SNAPSHOT_AND_SCORING_CONTRACT.md`](V2_CSC_GOVERNANCE_SNAPSHOT_AND_SCORING_CONTRACT.md).
It binds future scoring to explicit versions and hashes, prohibits implicit
cross-version blending, and preserves historical non-retroactivity. It is not
yet enforced by the current v1 enterprise reference scorer.

## Publication Identifiers

The immutable local source baseline is identified in
[`SOURCE_PROVENANCE.json`](../../SOURCE_PROVENANCE.json). The final public v2
commit, tag, ZIP checksum, publication inventory, evidence-pack identifier,
and APOD-TR-010 binding are not yet created at M09 and shall not be invented.

## Human Authority

The designated human release authority approves gate transitions, licence and
claim treatment, public commits, tags, assets, and publication. Automated
checks and AI-assisted work provide evidence and assistance only.
