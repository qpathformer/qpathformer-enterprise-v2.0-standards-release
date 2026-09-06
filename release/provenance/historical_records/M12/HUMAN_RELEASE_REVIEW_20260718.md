# Q-Pathformer Enterprise v2 Human Release Review

## Review Status

- Document ID: `QPATH-V2-M12-HUMAN-REVIEW-001`
- Phase: `M12`
- Mode: `A_release_candidate`
- Result: `HOLD`
- Reviewer: `PENDING_HUMAN_REVIEWER`
- Reviewer authority: `NOT_RECORDED`
- Approval reference: `NOT_RECORDED`
- Next authorized phase: `NONE`

This record is outside the frozen target. The `HOLD` result records the current
absence of a human disposition and three technical findings that affect
licensing or supply-chain integrity. It does not modify or invalidate the M11
byte identity; it prevents progression from that candidate.

## Candidate Binding

- Target: `C:\qpathformer_enterprise_v2_release`
- Target state: `M11_frozen_ready_for_human_release_review`
- Source-baseline commit: `cf9721afb81273d82667dd7b33ee5e5f3ad806d9`
- Source-baseline tag: `v2.0-qpathformer-enterprise-source-baseline`
- Source Git tree: `866cb4246d4fdc5e31c3a8be32249dc1b00b60ec`
- Publication inventory SHA-256: `875dd343ce1a730b1db58b7b2edf6af4e90ed3db3197687c0e7bc448dde95fea`
- SHA-256 set digest: `7fbc1f1a86de783ac7e4d4244ce76123f7a59a795d2ab477fd67fa144373ebd4`
- Frozen tree SHA-256: `ef86494a1009d6c526211d9efa3b81fdcd2ed45624c163c68c55f8443f07f961`
- Regular files: `351`
- Bytes: `35,757,693`

## Technical Review Outcome

Independent verification passed for every frozen byte, inventory entry,
checksum entry, JSON file, JSONL record, source anchor, and claim boundary.
The model references and non-distribution statements also match the official
model sources reviewed on 18 July 2026.

The candidate remains on hold for these findings:

1. `M12-F01` (`P1`): `QPATHFORMER-PLATFORM-1.0.txt:1` uses a custom licence
   value as an SPDX short identifier without the required `LicenseRef-` form.
2. `M12-F02` (`P1`): `docs/execution/DOWNLOAD_MODEL.md:73` executes a mutable
   remote installer through `irm ... | iex` with `ExecutionPolicy ByPass`.
3. `M12-F03` (`P2`): `.github/workflows/release-validation.yml:17` and `:20`
   reference GitHub Actions by movable major-version tags rather than full
   commit SHAs.

Full evidence and recommended dispositions are in
`V2_M12_TECHNICAL_REVIEW_REPORT.json`.

## Technical Recommendation

Return to M09 only for `M12-F01` through `M12-F03`. After those bounded
changes, rerun M10, rebuild the M11 inventory and checksums, and repeat M12
against the new frozen digest.

No Git initialization, commit, tag, ZIP, push, release asset, or APOD-TR-010
publication is authorized by this record.

## Human Decision

The designated human reviewer shall replace the pending fields above and
record one decision below. Until then, `HOLD` remains effective.

```text
reviewer:
reviewer_authority:
review_timestamp_utc:
review_result: PASS | FAIL | HOLD
approved_or_rejected_next_action:
approval_reference:
exceptions_and_rationale:
```

Suggested bounded remediation authorization:

```text
I authorize return to M09 only for M12-F01 through M12-F03: correct the custom
SPDX identifier, remove the remote pipe-to-shell installer, and pin GitHub
Actions to reviewed full commit SHAs. Rerun M10 and rebuild M11 before M12 is
reconsidered. No commit, tag, ZIP, push, asset, or publication is authorized.
```
