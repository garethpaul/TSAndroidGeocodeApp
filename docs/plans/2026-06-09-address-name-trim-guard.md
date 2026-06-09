# Address Name Trim Guard

## Status: Completed

## Context

`MainActivityWithAsyncTask` trims address-name input before starting geocoder
work, but the primary `MainActivity` service path only checks the raw
`EditText` length. Whitespace-only address input can still start the
`GeocodeAddressIntentService`.

## Objectives

- Keep the legacy address-name geocode flow intact.
- Trim address-name text before validating and passing it to the service.
- Preserve existing user feedback for blank address names.
- Extend the static Android contract checker to require the trim guard.

## Work Completed

- Trimmed primary `MainActivity` address-name input before validation.
- Passed the trimmed address name into `GeocodeAddressIntentService`.
- Extended `scripts/check_android_contracts.py` to preserve the trim guard.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`
