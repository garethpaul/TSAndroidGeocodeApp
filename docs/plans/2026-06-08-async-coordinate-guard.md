# Async Coordinate Guard

## Status: Completed

## Context

`MainActivity` already guarded invalid latitude/longitude text before starting
the geocode service. The older `MainActivityWithAsyncTask` variant still parsed
the coordinate `EditText` values inside `doInBackground`, so malformed input
could crash the task and UI state was read from the background path.

## Objectives

- Preserve the legacy AsyncTask geocode variant.
- Validate blank and malformed coordinate input before starting background work.
- Pass validated address/coordinate values into the AsyncTask.
- Keep the static Android contract checker covering both activity variants.

## Work Completed

- Added click-path validation and user feedback in `MainActivityWithAsyncTask`.
- Added a `GeocodeAsyncTask` constructor that captures validated request values.
- Removed background parsing of coordinate text fields.
- Extended `scripts/check_android_contracts.py` to preserve the async guard.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add Android Studio/device verification with a matching legacy SDK.
- Add README notes describing the address and coordinate geocoding flows.
