# Address Line Index Guard

## Status: Completed

## Context

Android `Address.getMaxAddressLineIndex()` returns the highest available
address-line index, not the number of address lines. The service and legacy
AsyncTask display paths used an exclusive loop bound, so a one-line geocoder
result could produce an empty rendered address.

## Objectives

- Include the final address line when rendering geocoder results.
- Preserve the primary IntentService and legacy AsyncTask result flows.
- Extend static Android contract checks so inclusive address-line iteration
  remains covered by `make check`.

## Work Completed

- Updated the service debug and result-fragment loops to include the maximum
  address-line index.
- Updated the legacy AsyncTask result display loop to include the maximum
  address-line index.
- Extended `scripts/check_android_contracts.py` to require inclusive
  address-line result loops.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check before implementation:
  `make check` failed with
  `async activity must include the final address line when rendering results`.
- `python3 scripts/check_android_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add device-backed geocoder result tests when a compatible Android SDK is
  available.
- Consider extracting shared address-line formatting if this sample is rebuilt.
