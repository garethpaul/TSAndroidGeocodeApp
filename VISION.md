## TS Android Geocode App Vision

TS Android Geocode App is a sparse Android geocoding sample with Gradle
configuration, a manifest, internet permission, and declared activity/service
entry points.

The repository is useful as a partial archive of an Android geocode app
structure, but the primary source files are not present in the current tree.

The goal is to preserve what exists and document the missing implementation
before adding new behavior.

The current focus is:

Priority:

- Preserve the Gradle and manifest structure
- Keep internet permission and service declarations visible
- Avoid inventing geocoding behavior that is not checked in
- Treat Android SDK and support library versions as legacy

Next priorities:

- Add README notes describing the intended geocoding flow
- Restore or document the missing activity and service source files
- Add setup notes for Android SDK versions
- Decide whether to archive or rebuild the sample

Contribution rules:

- One PR = one focused source restoration, manifest, build, or documentation change.
- Do not add API keys or user location data.
- Document any restored source provenance.
- Keep behavior claims aligned with checked-in code.

## Security And Responsible Use

Geocoding apps may process user-entered addresses or location data. Future
implementation should keep data handling explicit and avoid silent uploads or
retention.

## What We Will Not Merge (For Now)

- Claims about working geocoding before source is restored
- Checked-in geocoding API keys
- Silent location or address storage
- Broad rewrites without documenting missing source
