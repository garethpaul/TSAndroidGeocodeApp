# Service Coordinate Range Guard

## Status: Completed

## Context

The activity paths reject out-of-range latitude and longitude before starting
geocoder work. The `GeocodeAddressIntentService` still accepted coordinate
extras directly and relied on `Geocoder.getFromLocation()` to throw for invalid
ranges, which left direct service callers on a background exception path.

## Objectives

- Reject service coordinate extras outside latitude -90..90 and longitude
  -180..180.
- Avoid calling `Geocoder.getFromLocation()` for invalid service coordinates.
- Keep the existing invalid-coordinate failure message.
- Extend static checks so the service-side guard is preserved.

## Work Completed

- Added `isCoordinateInRange()` to `GeocodeAddressIntentService`.
- Guarded direct service coordinate extras before the geocoder lookup.
- Kept the existing `IllegalArgumentException` catch as a defensive fallback.
- Extended `scripts/check_android_contracts.py` to require service-side range
  limits and ordering before `getFromLocation()`.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add instrumentation tests when a compatible Android SDK is available.
- Add UI helper text that states the accepted latitude and longitude ranges.
