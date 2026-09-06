# Historical TR010 Document Seal

Status: **Verified historical integrity record, not a seal of this repository.**

The user supplied the July 21 document archive before the initial private
baseline commit. Its SHA-256 matches both the original external manifest and
the companion checksum file. All five content files match their internal
manifest sizes and SHA-256 values. The sixth ZIP member is the internal
manifest, which also matches its external sidecar byte-for-byte.

Archive: `sealed_20260721_100018.zip`, 1,192,359 bytes.
SHA-256: `9f61634e4493c2a2e8a5813b816c27f766fcf0c56d8a4c61e5a09db719f4adf2`.

## Retained Records

- [External manifest](manifest.external.json): unchanged historical archive identity and source locators.
- [Internal manifest](manifest.internal.json): unchanged identities of the five sealed files.
- [Companion checksum](sealed_20260721_100018.zip.sha256): unchanged ZIP checksum record.
- [Verification result](verification.json): measured archive/member hashes, copied-sidecar identities, and comparison with the selected private draft.

The ZIP and its historical manuscripts remain in the user's sealed-files
archive, not in Git. Original sidecars retain their historical machine paths.
The source archive and sidecars were not modified. These are additional
provenance records; they do not replace the initial source-selection catalogue.

## Draft Identity Boundary

The sealed rights/provenance-integrated manuscript is 593,599 bytes, SHA-256
`0faa2384b6f2ee3a31f11b67d3547112e6a5df9eeee42c67b17e62b9872e3c9d`.
The selected private working draft is 562,752 bytes, SHA-256
`44295dbe0cad76a6c4fc0edfe52a760070796d3f8c14d18cb63909fc4cf7883d`.
They are **not the same bytes**. Similar titles and dates do not establish
identity, content equivalence, or a direct revision relationship. The selected
draft remains unchanged and is not described as covered by this historical seal.

The selected draft's stored Word metadata records revision 38, last modified
`2026-07-21T19:10:00Z`, after the archive's recorded `10:00:18Z` seal time that
day. The sealed integrated manuscript retains revision 37 metadata. This supports
using the selected draft as the later working copy; stored application metadata
is not an independently authenticated timestamp or a content-difference review.

Hashes establish consistency with the supplied records, not independent
authentication, trusted timestamping, rights clearance, or publication approval.
GitHub CI can inspect the copied JSON records but cannot re-read the external
ZIP. A future release needs its own approved scope, inventory and integrity record.
