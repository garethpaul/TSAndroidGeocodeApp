---
title: Single In-Flight Geocode Request
date: 2026-06-13
type: implementation-plan
status: planned
---

# Single In-Flight Geocode Request

## Status: Planned

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
- R3. Disable the button immediately before a validated service dispatch.
- R4. Re-enable the button in the shared result-rendering path for successful,
  failed, null, and malformed delivered payloads.
- R5. Preserve progress visibility, weak Activity result delivery, privacy,
  typed receiver extraction, and input validation behavior.
- R6. Add mutation-sensitive static contracts and maintenance documentation.

## Key Technical Decisions

- **Use the existing action control as the guard.** Disabling the button is
  visible, accessible platform behavior and avoids adding parallel boolean
  state that could drift.
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

- A service that never delivers a result leaves the prior Activity button
  disabled. This change intentionally follows the existing result contract;
  service timeout/cancellation requires a separate lifecycle design.
- Disabling before validation would trap users after correctable input errors.
  Static ordering contracts will require the guard after all early returns.

## Verification

- Focused static contracts and hostile ordering/restoration mutations.
- Full `make check` with JDK 17 and Android SDK 36, plus a non-incremental
  Gradle unit-test, assemble, and lint invocation under explicit timeouts.
- Java/Python syntax, workflow YAML, Android XML, artifact, whitespace,
  intended-path, and changed-line secret audits.
