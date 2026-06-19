---
title: "fix: Read the geocode receiver through a typed compat API"
type: fix
date: 2026-06-13
---

# Read the Geocode Receiver Through a Typed Compat API

## Status: Completed

## Context

The geocode service still reads its `ResultReceiver` with Android's deprecated
untyped `Intent.getParcelableExtra(String)` method. The project already resolves
AndroidX Core 1.13.0 through AppCompat, which provides `IntentCompat` for a typed
API that works across the app's API 21-36 range.

## Requirements

- R1. Read the receiver with `IntentCompat.getParcelableExtra` and the explicit
  `ResultReceiver.class` token.
- R2. Preserve the existing missing-receiver guard and all result delivery.
- R3. Remove use of the deprecated untyped parcelable-extra method.
- R4. Protect the source contract with static mutation coverage and a complete
  Android build/lint gate.
- R5. Record the compatibility boundary without claiming lifecycle or service
  architecture modernization.

## Scope Boundaries

This change updates only parcelable extraction. Replacing `IntentService`,
changing the geocoding API, introducing WorkManager, or altering activity result
delivery remains outside scope.

## Implementation Units

### U1. Use Typed Compat Extraction

- **Goal:** Remove the deprecated untyped receiver read while preserving
  behavior across supported Android releases.
- **Files:** `app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeAddressIntentService.java`
- **Approach:** Import AndroidX `IntentCompat` and read the receiver with its
  generic typed overload before the existing null guard.
- **Test scenarios:** The full Android compile succeeds against the resolved
  Core 1.13.0 API; the source contains the receiver class token; the deprecated
  one-argument read is absent.
- **Verification:** Debug unit tests, APK assembly, and lint warnings-as-errors
  pass with JDK 17 and SDK 36.

### U2. Extend Static Contracts

- **Goal:** Prevent a regression to the deprecated or untyped API.
- **Files:** `scripts/check_android_contracts.py`
- **Approach:** Require the compat import and typed call, and explicitly reject
  the legacy call shape.
- **Test scenarios:** Mutations removing the import, class token, or compat call
  and restoring the legacy call are rejected.
- **Verification:** The static checker reports each weakened contract.

### U3. Document the Compatibility Update

- **Goal:** Record the completed modernization and actual verification.
- **Files:** `README.md`, `CHANGES.md`, `VISION.md`,
  `docs/plans/2026-06-13-typed-result-receiver-extra.md`
- **Approach:** Describe typed parcelable extraction as a compatibility fix,
  while keeping the larger deprecated-service risk visible.
- **Test expectation:** Documentation is enforced by the completed-plan
  checker; no separate runtime behavior is introduced.
- **Verification:** Documentation matches the implemented scope and commands.

## Risks

- Removing the null guard would turn a malformed service request into a crash.
- Using the platform API directly would require version branching; the compat
  API avoids duplicating that logic.
- The service class itself remains deprecated and requires a separate design.

## Assumptions

- AppCompat 1.7.1 continues to resolve AndroidX Core 1.13.0, whose compiled AAR
  exposes the typed `IntentCompat.getParcelableExtra` overload.

## Work Completed

- Replaced the deprecated untyped parcelable read with AndroidX
  `IntentCompat.getParcelableExtra`.
- Supplied `ResultReceiver.class` so the compatibility layer performs a typed
  read across API 21-36.
- Preserved the existing missing-receiver guard before geocoder construction.
- Added contracts requiring the compat import, typed call, class token, legacy
  call prohibition, and null guard.
- Updated behavior, limitation, vision, and change documentation while leaving
  the deprecated service architecture visible as follow-up work.

## Verification

- Amazon Corretto JDK 17.0.19 and Android SDK platform 36
- Resolved AndroidX Core 1.13.0 AAR inspected with `javap` for the typed overload
- Five focused static mutations rejected
- `make check` (five JVM tests, debug APK assembly, lint warnings-as-errors)
- External-directory `make check`
- `git diff --check`

No emulator, device geocoder, API key, or user location data is used by these
checks.
