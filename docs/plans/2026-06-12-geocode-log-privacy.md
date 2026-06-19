# Geocode Log Privacy

## Status: Completed

## Context

The geocode service wrote rejected latitude/longitude values and every resolved
street-address line to Android Logcat. Addresses and coordinates are sensitive
user-provided location data, and debug logs can persist beyond the visible app
session or be collected with diagnostic reports.

## Objectives

- Keep user-entered coordinates out of service logs.
- Keep resolved address lines out of service logs.
- Retain generic failure diagnostics and the visible geocode result.
- Protect the privacy boundary with repository contracts.

## Work Completed

- Removed latitude and longitude values from validation and geocoder-exception
  log messages.
- Removed the diagnostic loop that logged every resolved address line.
- Preserved generic error messages, exception context, and delivery of the
  first address result to the requesting activity.
- Updated the static checker to reject coordinate and address-result logging.
- Updated security, maintenance, vision, and change documentation.

## Verification

- `python3 scripts/check_android_contracts.py` passed all seven static contract
  groups.
- `make check` passed with Temurin 17 and the local Android SDK, executing
  `testDebugUnitTest`, `assembleDebug`, and `lintDebug` across 46 Gradle tasks.
- `make -C TSAndroidGeocodeApp check` passed from the checkout's parent
  directory with the same toolchain.
- Five hostile mutations were rejected: coordinate logging, resolved-address
  object logging, address-line logging, excluding the final address line, and
  changing this plan from completed to planned.
- `git diff --check` passed.

No real location, address, device, or network geocoding service is used by the
portable tests.
