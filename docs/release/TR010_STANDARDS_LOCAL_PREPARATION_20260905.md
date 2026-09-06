# TR010 Standards Local Preparation

Date: 2026-09-05. Label: `TR010-STANDARDS-LOCAL-20260905`.

**Status: local development review candidate; not an official release, lawyer-reviewed package, certification or publication approval.**

## Decision and Scope

The owner authorized starting the standards-focused work locally and refining TR010 with a Markdown record of every paper edit. This implements the bounded CORE-01 to CORE-04 slice and adds a dated CORE-05 claim/evidence supplement. It does not restart M00 or create another release-phase ladder.

The private repository remains the development source. Parent HEAD is `57c7fbbed476a8f74ba4ca7b6acb495791ba5524`; the changes in this record are **uncommitted** and are identified by the [scoped source inventory](../../evidence/v2_validation/standards_local_20260905/source_inventory.json), not by pretending that the parent commit includes them.

No commit, tag, ZIP, push, public-repository transition, licence adoption, actual training or new CSC scoring was performed. `shared/standards`, historical evidence, the original TR010 manuscript and their original provenance records are retained unchanged.

## Implemented Controls

| Requirement | Implementation | Executed evidence |
|---|---|---|
| CORE-01 Single-scope | `scripts/training_authorization.py`, authorization creator and schema now use `qpath_training_authorization_v2.2`. ALLOW has one explicit scope; DENY has none. | `test_standards_single_scope.py` checks builder/schema/verifier cardinality, unknown values, denial and legacy rejection. |
| CORE-02 Endpoint binding | Preparation, copy-migration and local LoRA are bound to `validation_parameter_update`. Caller labels cannot substitute another operation. | Wrong-operation requests fail before registry/package access; even a correctly signed and sealed production-scoped package cannot enter the research backend. |
| CORE-03 Rejection outputs | The local runner resolves its supported log route before creating its final run directory. Existing authorization and seal checks remain before backend execution. | Invalid authorization, validity, binding, role-key, route and tamper cases assert no final success directory/backend entry. This is bounded coverage, not universal side-effect freedom. |
| CORE-04 Reproduction | A temporary four-record fixture, disposable distinct keys and real CLI subprocesses exercise signed/sealed preparation and dry-run execution. | Nine expected CLI outcomes; exact commands and hashes retained in the rehearsal report. |
| CORE-05 Paper reconciliation | A separate dated paper revision and full before/after Markdown record distinguish current tests from historical July evidence. | Original paper hash retained; revision identity is separately allowlisted. Professional review is explicitly policy-level, not an implemented legal-status check. |

Legacy v2.1 authorization artifacts require a fresh decision, new signature and new sealed copy. They are not edited or accepted implicitly. Single-scope does not provide one-time use, revocation, replay protection or named-run consumption.

## Results and Reproduction

| Check | Local outcome |
|---|---|
| Before this slice | 33 tests: 32 passed, one Windows symlink-capability skip. |
| After this slice | 48 tests: 47 passed, one Windows symlink-capability skip, zero failures. |
| Isolated CLI rehearsal | Nine of nine expected outcomes, including intentionally rejected requests. |
| Model execution | None. Successful execution is explicitly a dry run. |
| Complete three-path replay | Not performed; the rehearsal starts from synthetic frozen/registered fixtures. |
| Hosted CI | Not rerun in this local preparation task. |
| Paper layout | Word export produced 379 pages; all were rasterized and the 18 identified edit/boundary pages were visually checked. Full-manuscript and TOC review remain open. |

Use the [reference runbook](../execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md). Machine-readable records and logs are in [the evidence directory](../../evidence/v2_validation/standards_local_20260905/README.md). The skipped test is not passed coverage. Historical 24-test, export and M11 figures in TR010 are not replaced by, or attributed to, this development run.

## Legal Profession and AI Boundary

The proposed profile requires practitioner review before rights-dependent activity beyond synthetic local testing. That review concerns identified materials, intended uses, relevant jurisdictions, permissions, restrictions and unresolved exceptions. The organization's named-operation decision remains separate. Neither a lawyer's review nor an organizational decision creates missing third-party rights.

The profile does not approve automated AI legal review as a substitute for a qualified practitioner. It does not prohibit supervised AI assistance. Professional responsibility and independent verification remain with the practitioner when using AI, consistent with the [joint NSW, Victorian and Western Australian regulatory statement](https://www.lawsociety.com.au/sites/default/files/2024-12/LS4590_PSP_Statement_AI_LawSocietyVersion.pdf).

For a real engagement, verify professional entitlement for the relevant jurisdiction and scope rather than accepting a generic "certified reviewer" label. See the [Law Society of NSW's explanation of unqualified practice](https://www.lawsociety.com.au/practising-law-in-NSW/complaints-and-discipline/unqualified-practitioners). The applicable licence, permission or exception must still support the proposed use; see [Attorney-General's Department guidance for copyright users](https://www.ag.gov.au/rights-and-protections/copyright/copyright-users).

TR010 now proposes possible practitioner services in rights mapping, exception resolution, licensing conditions and periodic reassessment. This is a service-design proposition, not evidence that AI has made lawyers redundant or that a particular market outcome will occur. Confidential advice should remain outside the Git package; an appropriately approved bounded review record can reference it without publishing privileged content.

**Current limitation:** reviewer metadata and cryptographic signatures do not verify practitioner credentials, retainer scope, legal conclusions, delegation or satisfaction of free-text conditions. No actual lawyer review is recorded and no replacement licence is adopted. The technical rehearsal must not be described as lawyer reviewed.

## Review Before Official Release

Continue with focused review, not another full historical gate cycle. The remaining work is to review the code diff and paper edits, finish manuscript/TOC layout review, reconcile proposed TR010-R claims to these exact source hashes, and resolve the file-specific rights/distribution schedule with appropriate professional input before the proposed rights-dependent release use. Hosted CI should be rerun only following the separately authorized Git action.

Retain the operative licence and all historical notices while review is pending. The separate [licensed-service plan](TR010_LICENSED_SERVICE_DEVELOPMENT_RELEASE_PLAN.md) is still a plan, not a launched or lawyer-approved service. Eventual official publication needs an explicitly selected identity and owner authorization; no public release tag is assigned here.
