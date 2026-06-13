---
title: Single In-Flight Geocode Request
date: 2026-06-13
type: implementation-plan
status: completed
---

# Single In-Flight Geocode Request

## Status: Completed

## Summary

Prevent repeated action-button taps from starting overlapping geocoder service
requests in the same Activity instance. Keep the control available for all
validation failures, disable it only for a dispatched request, and restore it
for every delivered success or failure result.

## Problem Frame

`MainActivity.onButtonClicked` shows progress and starts the service without
disabling the action button. A user can therefore dispatch multiple requests
while the first is active, consuming duplicate geocoder work and allowing
completion order rather than user intent to determine the final visible result.

## Requirements

- R1. Retain the action button as Activity state so result handling can restore
  it without another view lookup.
- R2. Leave the button enabled for blank, malformed, out-of-range, and
  unavailable-geocoder failures that do not start the service.
- R3. Disable the button immediately after a validated service dispatch
  succeeds, before the click handler returns to the event loop.
- R4. Re-enable the button in the shared result-rendering path for successful,
  failed, null, and malformed delivered payloads.
- R5. Preserve progress visibility, weak Activity result delivery, privacy,
  typed receiver extraction, and input validation behavior.
- R6. Add mutation-sensitive static contracts and maintenance documentation.

## Key Technical Decisions

- **Use the existing action control as the guard.** Disabling the button is
  visible, accessible platform behavior and avoids adding parallel boolean
  state that could drift.
- **Disable after successful startup.** The UI thread cannot process another
  tap within the current click callback, and this ordering avoids stranding the
  control if `startService` throws before accepting the request.
- **Restore through `showResultText`.** Every handled result already converges
  there, so one restoration point covers success and all delivered failures.
- **Do not persist in-flight state across recreation.** The receiver is tied to
  the prior Activity by a weak reference; a recreated Activity should remain
  usable rather than inherit an unobservable request lock.

## Scope Boundaries

This change does not replace `IntentService`, add request identifiers,
cancellation, a queue, device geocoder tests, or cross-recreation result
delivery. It does not change service payloads or geocoding semantics.

## Implementation Units

### U1. Guard request dispatch

- **Files:** `app/src/main/java/com/sample/foo/tsgeocodeapp/MainActivity.java`
- Store the action button during view binding, use it for listener setup, and
  disable it only after validation and availability checks succeed.

### U2. Restore interaction and enforce contracts

- **Files:** `MainActivity.java`, `scripts/check_android_contracts.py`
- Re-enable through the shared renderer and require binding, ordering,
  dispatch disablement, and result restoration with hostile mutations.

### U3. Complete maintenance evidence

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-13-single-inflight-geocode-request.md`
- Record behavior, full Android verification, mutation results, structured
  audits, and remaining device/emulator limits.

## Risks And Mitigations

- A service that starts but never delivers a result leaves the prior Activity button
  disabled. This change intentionally follows the existing result contract;
  service timeout/cancellation requires a separate lifecycle design.
- Disabling before validation or before service acceptance would trap users
  after correctable input or startup errors. Static ordering contracts require
  the guard after all early returns and the successful `startService` call.

## Verification

- A disposable exact-source snapshot passed `make check` with Temurin JDK 17
  and Android SDK 36: seven static contract groups, five JVM tests, debug APK
  assembly, and Android lint with warnings treated as errors.
- The repository gate and a non-incremental Gradle `testDebugUnitTest
  assembleDebug lintDebug` invocation also passed under 300-second timeouts.
- Eight hostile mutations covering button binding, dispatch ordering,
  restoration, documentation, and completed plan status were rejected.
- Review moved disablement after successful service startup so a thrown startup
  error cannot leave the action control stranded; the UI thread still applies
  the guard before another tap can be dispatched.
- Python syntax, workflow and Dependabot YAML, Android XML, exact-path,
  generated-artifact, whitespace, and changed-line secret audits passed.
- Device/emulator geocoder delivery and a service that never sends a result
  remain outside local coverage; the latter can leave the prior Activity's
  action button disabled until recreation.
