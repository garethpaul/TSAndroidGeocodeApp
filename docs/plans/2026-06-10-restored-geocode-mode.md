# Restored Geocode Mode

Status: Completed

## Goal

Keep the geocode request type aligned with the radio selection Android restores
when `MainActivity` is recreated.

## Implementation

- Remove the recreation-prone `fetchType` activity field.
- Derive the fetch type from the checked address radio button for every request.
- Keep radio click handling limited to enabling the matching input controls.
- Extend static contracts to require restored-view-state ownership of the mode.

## Verification

- `make static`
- `make check`
- Mutation check: restoring a default `fetchType` field must fail the static
  lifecycle contract.
