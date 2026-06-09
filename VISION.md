## TS Android Geocode App Vision

TS Android Geocode App is a sparse Android geocoding sample with Gradle
configuration, a manifest, internet permission, and declared activity/service
entry points.

The repository is useful as a partial archive of an Android geocode app
structure with checked-in activity and service source files.

The goal is to preserve what exists, keep the legacy behavior understandable,
and make small defensive improvements without broad rewrites.

The current focus is:

Priority:

- Preserve the Gradle and manifest structure
- Keep internet permission and service declarations visible
- Keep geocoding behavior claims aligned with checked-in code
- Treat Android SDK and support library versions as legacy
- Keep Gradle application id aligned with the manifest package
- Guard user-entered coordinates before invoking geocoder services
- Keep background geocode tasks consuming validated request values
- Keep completed maintenance plans under `docs/plans`

Next priorities:

- Add README notes describing the intended geocoding flow
- Add focused checks for UI and service contracts
- Add setup notes for Android SDK versions
- Decide whether to archive or rebuild the sample

Contribution rules:

- One PR = one focused source restoration, manifest, build, or documentation change.
- Do not add API keys or user location data.
- Document any restored source provenance.
- Keep behavior claims aligned with checked-in code.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Geocoding apps may process user-entered addresses or location data. Future
implementation should keep data handling explicit and avoid silent uploads or
retention.

## What We Will Not Merge (For Now)

- Claims about production-ready geocoding without current device verification
- Checked-in geocoding API keys
- Silent location or address storage
- Broad rewrites without documenting missing source

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
