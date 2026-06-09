# Service Address Name Guard

## Status: Completed

## Context

The primary activity trims and rejects blank address-name input before starting
the geocoding service. The `GeocodeAddressIntentService` still trusted the
incoming extra directly, which left direct service invocations or future
callers able to pass null or blank address names into `Geocoder`.

## Objectives

- Normalize address-name extras inside the service.
- Reject blank service address-name requests before geocoder work starts.
- Extend static Android contract checks so activity and service validation stay
  aligned.

## Work Completed

- Trimmed the service `LOCATION_NAME_DATA_EXTRA` value before use.
- Returned an invalid-address error path without calling `Geocoder` for blank
  service extras.
- Extended `scripts/check_android_contracts.py` to require service-side
  address-name normalization and rejection.
- Updated README, VISION, and CHANGES with the new guardrail.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add service-level coordinate range validation for direct IntentService
  callers.
- Add Android instrumentation tests when the legacy SDK setup is available.
