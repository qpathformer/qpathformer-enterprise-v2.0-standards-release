# V2 CSC Governance Snapshot And Scoring Contract

## Status

This document defines the v2 governance and scoring design baseline. It does
not activate a new scorer, recalculate historical v1.0 CSC results, or create
a v2 CSC Assurance Record. Enforcement and calibration remain a later
implementation gate.

The machine-readable companion is
[`release/V2_CSC_GOVERNANCE_SNAPSHOT_CONTRACT.json`](../../release/V2_CSC_GOVERNANCE_SNAPSHOT_CONTRACT.json).

## Purpose

The v2 snapshot separates four evidence layers:

1. The preserved Access-PoD v1a public-review contracts.
2. The v1 enterprise profile, mapper, evidence-input, and execution bridge.
3. Qualified historical v1.0 CSC results.
4. New v2 governance and scoring rules.

These layers may be linked, but they shall not be merged into an unversioned
catalogue or treated as one indistinguishable scoring source.

## Canonical V1a Treatment

Three vendored v1a files are byte-exact matches to
`manifest_v1a_pack.json`. Six files differ physically only because their line
endings are CRLF rather than LF. Applying only `CRLF -> LF` to each of those
six files reproduces the exact manifest byte count and SHA-256.

The release therefore retains the physical historical bytes and records:

- the physical byte count and SHA-256;
- the canonical LF byte count and SHA-256;
- the original manifest byte count and SHA-256;
- whether the verification is `BYTE_MATCH` or `CANONICAL_LF_MATCH`.

No JSON reserialization, whitespace trimming, Unicode normalization, PDF
rewriting, field reordering, or semantic transformation is permitted by this
equivalence rule.

## Snapshot Identity

Every future v2 CSC Assurance Record shall bind the following by identifier,
version, path or URI, byte count, and SHA-256:

- metric catalogue;
- certificate or Assurance Record schema;
- sector profile;
- mapper or evidence crosswalk;
- scoring policy;
- implementation version;
- run and session provenance;
- evidence window;
- evidence bundle and signature state.

A missing or mismatched binding produces `insufficient_evidence`; it shall not
fall back to a default policy.

## Observation Status

Each applicable metric shall declare exactly one status:

- `observed`: qualifying evidence exists and a numeric value may be used.
- `insufficient_evidence`: evidence exists but cannot support a numeric value.
- `unobserved`: no qualifying observation exists.
- `not_applicable`: excluded only with a governed justification.
- `suspended`: previously usable evidence is temporarily ineligible.

Numeric values are prohibited for `insufficient_evidence`, `unobserved`, and
`suspended`. Missing observations are never imputed as zero.

## Evidence Classification

Every observed metric shall separate:

- direct telemetry;
- proxy evidence;
- derived evidence;
- excluded evidence.

The record shall expose direct, proxy, derived, observed, applicable,
unobserved, and excluded counts. Proxy evidence shall not be presented as
direct telemetry.

## Coverage

Coverage is calculated against the active, bound catalogue and the metrics
applicable to the selected profile:

```text
applicable_metric_count = catalogue_metric_count - approved_not_applicable_count
observed_coverage = observed_metric_count / applicable_metric_count
direct_telemetry_ratio = direct_telemetry_count / observed_metric_count
proxy_evidence_ratio = proxy_evidence_count / observed_metric_count
```

If an older evidence record is evaluated against a newer catalogue, newly
required metrics begin as `unobserved`. This lowers coverage and confidence,
not the historical raw measurement value. Historical scores remain bound to
their original snapshot and are not retroactively replaced.

## Score Surfaces

V2 separates three values:

- `raw_observed_score`: weighted score over eligible observed metrics.
- `confidence_adjusted_score`: raw factor contributions multiplied by their
  qualified confidence, without renormalizing away uncertainty.
- `maximum_permissible_level`: the strictest cap produced by coverage, direct
  telemetry, independent observation windows, sector validation, and
  mandatory gates.

The displayed v2 level shall use the confidence-adjusted score and shall not
exceed the maximum permissible level.

## Confidence

Factor confidence shall account for:

- observation confidence;
- applicable-metric coverage;
- direct-versus-proxy evidence ratio;
- evidence freshness;
- independent observation windows;
- unresolved exclusions or contradictions.

The exact coefficients and cap thresholds require a separately versioned and
calibrated policy. V2 fails closed while that policy is absent; the legacy v1
defaults are not inherited automatically.

## Cross-Version Rule

Implicit cross-version scoring is prohibited.

Evidence from different catalogue, schema, profile, or policy versions may be
used together only through a versioned crosswalk that declares:

- source and target metric identifiers;
- semantic equivalence or transformation;
- evidence-loss behavior;
- confidence penalty;
- incompatible or newly required metrics;
- approval authority and effective period.

Without an approved crosswalk, the records remain separate snapshots.

## Historical Non-Retroactivity

The Finance, Healthcare, Public, and AI/emerging-technology values in
`release/V1_CSC_EVIDENCE_MANIFEST.json` remain qualified historical v1.0
outputs. V2 may display their limitations but shall not silently rescore,
upgrade, downgrade, or relabel them.

## Enforcement Boundary

The current `build_csc_certificate.py` implementation is a v1 enterprise
reference scorer. It does not yet enforce the complete observation-status,
crosswalk, confidence-adjustment, or maximum-level contract defined here.
Until that later implementation passes its own schemas, tests, calibration,
and review gate, no output may claim conformance with the v2 scoring contract.
