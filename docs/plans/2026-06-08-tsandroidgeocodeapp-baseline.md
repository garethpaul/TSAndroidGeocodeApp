# TSAndroidGeocodeApp Baseline

## Status: Completed

## Context

`TSAndroidGeocodeApp` is a legacy Android geocoding sample with checked-in
activity, service, manifest, and Gradle module files. The maintenance baseline
should keep package identity and coordinate input handling checked without
requiring a full legacy Android build.

## Objectives

- Preserve manifest, activity, and geocode service declarations.
- Keep Gradle `applicationId` aligned with the manifest package and Java
  package.
- Validate XML resources and user feedback for invalid coordinates.
- Run static Android contract checks through `make check`.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs the static Android contract checker and skips the
  Android build when no wrapper/root settings are checked in.
- Added canonical `docs/plans` coverage for the current geocode baseline.
- Extended the contract checker to require completed `docs/plans` entries with
  `make check` verification.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add README notes describing the intended geocoding flow.
- Run Android Studio/device verification with matching legacy SDK tooling.
