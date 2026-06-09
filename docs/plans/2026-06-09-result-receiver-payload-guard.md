# Result Receiver Payload Guard

## Status: Completed

## Context

`MainActivity.AddressResultReceiver` rendered service results by assuming the
result bundle, returned `Address`, and result string were present. A malformed
or incomplete result could crash the UI while reading address coordinates or
render a null message. The sample should keep result display defensive even
when service calls fail or return incomplete data.

## Objectives

- Guard missing result bundles before reading payload fields.
- Guard successful results that lack an `Address` or display text.
- Use one UI rendering helper for success and failure messages.
- Keep the fallback result text explicit and static-checkable.
- Extend `make check` to preserve the receiver payload guard.

## Work Completed

- Added `NO_GEOCODE_RESULT` fallback text.
- Added `showResultText` to centralize progress/info visibility updates.
- Guarded null result bundles, null addresses, and blank result messages.
- Extended `scripts/check_android_contracts.py` to require the payload guard.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make check`
- `git diff --check`

Android build verification was skipped because this repository does not include
a Gradle wrapper or root `settings.gradle` file in this environment.

## Follow-Up Candidates

- Add README notes describing the expected service result lifecycle.
- Add device-backed result receiver tests if the legacy Android toolchain is
  restored.
