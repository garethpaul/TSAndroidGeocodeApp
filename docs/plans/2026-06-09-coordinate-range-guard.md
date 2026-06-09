# Coordinate Range Guard

## Status: Completed

## Context

The geocode sample already catches non-numeric latitude and longitude input
before starting geocoder work. Numeric but out-of-range values could still reach
the IntentService or AsyncTask path and rely on background `IllegalArgumentException`
handling instead of immediate user feedback.

## Objectives

- Reject latitude values outside -90..90 before geocoder work starts.
- Reject longitude values outside -180..180 before geocoder work starts.
- Apply the guard to both the IntentService and AsyncTask activity variants.
- Extend static checks so range validation is preserved.

## Work Completed

- Added `isCoordinateInRange` to `MainActivity`.
- Added `isCoordinateInRange` to `MainActivityWithAsyncTask`.
- Reused the existing invalid-coordinate user-facing string for out-of-range
  values.
- Extended `scripts/check_android_contracts.py` to require range guards before
  service or AsyncTask execution.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add instrumentation tests when a compatible Android SDK is available.
- Add UI helper text that states the accepted latitude and longitude ranges.
