# M12 Bounded Remediation Authorization

- Record ID: `QPATH-V2-M12-REMEDIATION-AUTH-001`
- Recorded date: `2026-07-18`
- Authority role: `Q-Pathformer Human Release Authority`
- Prior M12 result: `HOLD`
- Authorized return point: `M09`
- Authorized findings: `M12-F01`, `M12-F02`, `M12-F03`

## Human Authorization

> I authorize return to M09 only for M12-F01 through M12-F03: correct the
> custom SPDX identifier, remove the remote pipe-to-shell installer, and pin
> GitHub Actions to reviewed full commit SHAs. Rerun M10 and rebuild M11 before
> M12 is reconsidered. No commit, tag, ZIP, push, asset, or publication is
> authorized.

## Scope Interpretation

The licence correction changes only the SPDX metadata from
`QPATHFORMER-PLATFORM-1.0` to
`LicenseRef-QPATHFORMER-PLATFORM-1.0`. It does not change the Q-Pathformer
Platform License 1.0 text, rights, restrictions, copyright, ownership, or
application to the v2 repository.

This record authorizes the three bounded file corrections and regeneration of
the M10 and M11 evidence required to bind the corrected bytes. It does not
authorize M12 approval or any M13 action.
