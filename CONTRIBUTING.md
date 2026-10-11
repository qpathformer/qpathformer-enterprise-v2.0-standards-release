# Contributing to Q-Pathformer Enterprise v2.0 Standards Edition

This repository contains a bounded standards-exploration implementation, the
APOD-TR-010 paper pair and separately identified evidence. Start with the
[documentation index](docs/README.md) and
[local standards checks](docs/execution/LOCAL_CHECKS.md) before proposing work.

The [published v2.0 release](https://github.com/qpathformer/qpathformer-enterprise-v2.0-standards-release/releases/tag/v2.0-qpathformer-enterprise-standards)
is immutable. Later maintenance of `main` does not replace its tag, assets,
papers or evidence. Corrections and future implementation changes must be
identified separately from the published selection and its historical records.

## Normal change workflow

1. **Create a focused branch from current `main`.** For example, use
   `docs/clarify-authorization-evidence`. Contributors without write access can
   propose changes from a fork, subject to the applicable terms. Keep the
   published packages and preserved evidence separate from the working checkout.
2. **Prepare the change and identify its provenance.** Preserve original
   papers, artifacts, licence notices and attribution. Use errata, supplementary
   guidance or separately versioned additions for corrections. Identify any
   third-party material and confirm that you have permission to submit it.
3. **Run the relevant checks, then push the branch.** Follow
   [Repository checks](.github/CHECKS.md). Retain the existing synthetic
   development validation as well as the maintenance checks. Review the diff
   and record manual checks and any new observations under their actual scope.
4. **Open a draft pull request to `main`.** Explain the problem, resulting
   behavior, affected files, provenance and validation. Distinguish maintenance
   guidance from a future release proposal. Do not upload private datasets,
   credentials or restricted third-party content.
5. **Complete review and resolve feedback.** Mark the pull request ready when
   complete. Review the full diff, rights and attribution, preservation of
   original material, and all four required check results. Resolve conversations.
   If `main` advances, update the branch and wait for the checks to pass again.
6. **Merge deliberately.** An authorised maintainer performs the merge after
   review and passing checks. Squash merging is suitable for a focused change.
   Delete the completed working branch if no longer needed, then update local
   `main`. A merge is not release publication or operational authorization.

## Required checks and merge rules

Changes to `main` must use a pull request. All four exact GitHub Actions checks
must pass with the proposed branch up to date with `main`:

- **validate (ubuntu-latest)**
- **validate (windows-latest)**
- **README links**
- **JSON syntax**

Review conversations must be resolved. Force pushes and deletion of `main`
are blocked. The rules apply to administrators, with no configured
pull-request bypass. Existing restrictions on who may push to `main` and
dismiss reviews remain in place.

The current single-maintainer workflow requires **zero approving reviews**;
the authorised maintainer can merge their own pull request after the other
conditions are met. This records the proposal and review without representing
independent approval. Human review remains required by this workflow. An
independent approval requirement can be introduced when another eligible
reviewer is available.

The existing cross-platform development checks remain required; the new
maintenance checks do not replace them. Passing checks is evidence for the
tested selection and conditions, not independent assurance or permission to
publish, train, deploy or distribute material beyond the applicable terms.

## Preparation and publication are separate

The existing development workflow runs `tools/verify_private_workspace.py`
in preparation mode and the synthetic unit suite. It does not invoke
`--require-final-papers`. A preparation PASS is not readiness to seal or
publication permission.

The separate final-paper check verifies the registered PDF pair's identities.
It does not replace visual review, review of applicable rights, the named human
decision or a separate publication process. Do not change a paper, allowlist,
manifest or recorded hash merely to obtain a passing check. Follow the
[local standards guidance](docs/execution/LOCAL_CHECKS.md) for the distinction
between preparation, paper identity and historical-origin diagnostics.

## Licences and contribution scope

Read [LICENSE](LICENSE),
[Q-Pathformer Platform License 1.0](QPATHFORMER-PLATFORM-1.0.txt),
[NOTICE.md](NOTICE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Platform 1.0 remains the stated licence; Licence 1.1 and the historical
rights/provenance drafts have not been adopted. This guide adds no licence
grant and changes none of the existing terms.

Identify the source and applicable terms of contributed code, data and
documents. Preserve attribution and copyright notices, and disclose adapted
material. Explain any AI-assisted contribution so a maintainer can review its
sources, accuracy and suitability. Do not remove or bypass governance
safeguards. Public availability or acceptance of a pull request does not itself
provide additional redistribution or production rights.

The retained Access-PoD v1a subset has its own
[MIT licence](shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/LICENSE).
The maintenance helpers under `.github/ci/` separately carry their own scoped
[MIT notice](.github/ci/LICENSE), retained from the Access PoD helpers from
which they were adapted. Neither notice relicenses the platform, papers or
other artifacts. Existing file-specific and dependency terms remain applicable.

## Preserve published and historical records

- Keep `v2.0-qpathformer-enterprise-standards`, the immutable release and all
  published assets unchanged. Do not delete or recreate the release to change
  its content.
- Preserve the original paper pair, registered identities, vendored standards,
  provenance inventories, historical candidate records and earlier evidence.
  New maintenance documentation is not part of an earlier sealed inventory.
- Keep April v1.0 execution, July candidate work and September v2 observations
  distinct. A new test run is a new observation, not a replacement for retained
  totals or a retrospective change to an earlier decision.
- Record later experiments separately with their actual inputs, environment,
  commands, results and limitations. Keep generated rehearsal output outside
  the published selection unless separately reviewed.
- Prepare future editions through a separate versioned review and publication
  process, with new evidence, integrity records and an explicitly reviewed
  distribution scope.

Check that every pull-request diff contains only the intended changes. Later
publication work must also compare the existing release tag and asset
identities and hashes before and after the work.
