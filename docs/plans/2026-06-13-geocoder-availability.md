# Geocoder Availability Guard

## Status: In Progress

## Context

Android does not guarantee that a `Geocoder` backend exists on every device.
The activity currently starts background work unconditionally, and the service
then attempts synchronous geocoding even when the platform reports no backend.

## Priority

Failing before service startup gives users immediate stable feedback and avoids
unnecessary background lifecycle work. Rechecking in the service preserves a
defense-in-depth boundary if availability changes or another caller starts the
service directly.

## Requirements

- R1. Check `Geocoder.isPresent()` after input validation and before
  `startService`.
- R2. Show a localized stable unavailable message and leave the progress view
  hidden when the activity-side check fails.
- R3. Recheck availability in the service before constructing `Geocoder` or
  invoking either lookup API.
- R4. Deliver the existing failure result with the same localized message when
  the service-side check fails.
- R5. Preserve input validation, typed receiver extraction, weak activity
  ownership, privacy-safe logging, and successful geocode behavior.
- R6. Static contracts, documentation, and hostile mutations must preserve both
  availability boundaries.

## Implementation Units

### U1. Add activity and service guards

- **Files:** `MainActivity.java`, `GeocodeAddressIntentService.java`,
  `strings.xml`
- Add the platform availability checks and one shared localized message.

### U2. Extend repository verification

- **Files:** `scripts/check_android_contracts.py`
- Enforce check placement before service startup and before geocoder creation,
  plus failure delivery and localized-message use.

### U3. Document behavior and residual risk

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record the fail-fast behavior and retain device/emulator verification as a
  limitation.

## Scope Boundaries

- Do not replace `IntentService` or synchronous geocoder calls in this change.
- Do not add a dependency, permission, or network fallback provider.
- Do not alter accepted address or coordinate inputs.

## Verification

- Full `make check` with JDK 17 and Android SDK 36
- Static contract mutations removing, reordering, or bypassing either guard
- XML/YAML parsing, `git diff --check`, and focused secret/artifact review
