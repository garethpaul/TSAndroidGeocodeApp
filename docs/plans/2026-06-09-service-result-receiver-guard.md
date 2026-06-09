# IntentService ResultReceiver Guard

## Status: Completed

## Context

`GeocodeAddressIntentService` returns geocode results through the
`ResultReceiver` extra supplied by `MainActivity`. Direct or malformed service
invocations without that receiver should not perform geocoder work or reach
`resultReceiver.send(...)`.

## Objectives

- Preserve the existing activity-to-service geocode flow.
- Reject service requests that cannot receive a result.
- Guard the receiver before creating a `Geocoder`.
- Extend static checks so the guard is not removed.

## Work Completed

- Read the `ResultReceiver` extra at the start of `onHandleIntent()`.
- Added an early return when the receiver is missing.
- Moved `Geocoder` creation after the receiver guard.
- Extended `scripts/check_android_contracts.py` to require the guard before
  geocoder creation.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `python3 scripts/check_android_contracts.py` failed with
  `IntentService must reject requests without a ResultReceiver`.
- `python3 scripts/check_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Android Notes

No Gradle wrapper or root `settings.gradle` is checked in, so this environment
ran the repository static checks and skipped the Android build.
