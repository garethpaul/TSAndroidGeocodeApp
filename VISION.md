## TS Android Geocode App Vision

TS Android Geocode App is a small, reproducibly buildable Android geocoding
sample with a manifest, internet permission, and declared activity/service
entry points.

The repository is useful as an educational example of validating address or
coordinate input before delegating platform geocoder work to a service.

The goal is to preserve the sample's behavior while keeping its build,
dependencies, validation, and privacy defaults verifiable on supported tools.

The current focus is:

Priority:

- Preserve the Gradle and manifest structure
- Keep internet permission and service declarations visible
- Keep geocoding behavior claims aligned with checked-in code
- Keep the JDK 17, API 36, Gradle, and AndroidX toolchain reproducible
- Keep Gradle application id aligned with the manifest package
- Guard user-entered coordinates before invoking geocoder services
- Reject out-of-range coordinates before invoking geocoder services, including
  direct IntentService requests
- Trim and validate address-name requests before invoking geocoder services
- Keep background geocode work consuming validated request values
- Reject activity and direct-service requests when no platform geocoder exists
- Keep one in-flight geocoder request per Activity interaction surface
- Reject IntentService geocode requests that cannot receive a result
- Keep ResultReceiver extraction typed across supported Android releases
- Guard geocode result payloads before updating the primary activity UI
- Avoid retaining or updating stale activities while background geocode work
  is in progress
- Keep geocode request mode aligned with radio state restored after recreation
- Include the final Android address line when rendering geocode results
- Keep user-entered and resolved location data out of Logcat
- Keep Android app-data backup disabled by default
- Keep activity source aligned with declared layout widget ids
- Keep completed maintenance plans under `docs/plans`

Next priorities:

- Replace deprecated `IntentService` and synchronous geocoder calls if the
  sample receives further lifecycle-focused development
- Add emulator coverage for the activity/service result flow
- Verify behavior against multiple platform geocoder implementations

Contribution rules:

- One PR = one focused source restoration, manifest, build, or documentation change.
- Do not add API keys or user location data.
- Document any restored source provenance.
- Keep behavior claims aligned with checked-in code.
- Preserve trimmed address-name and coordinate validation before geocoder work.

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
- Out-of-range geocoder requests that rely on background exceptions
- Source references to undeclared layout widgets
- Broad rewrites without preserving the educational geocoding flow

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
