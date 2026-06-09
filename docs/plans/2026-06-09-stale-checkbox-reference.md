# Stale Checkbox Reference

## Status: Completed

## Context

Both activity variants referenced `R.id.checkbox`, but the checked-in
`activity_main.xml` layout does not declare a checkbox with that id. The field
was unused, so the reference only created a stale resource dependency and a
compile-risk for the legacy sample.

## Objectives

- Remove unused checkbox imports, fields, and `findViewById()` calls.
- Keep geocode form behavior unchanged.
- Add a static contract so source files do not reference undeclared checkbox
  ids.
- Record the cleanup in the repository maintenance docs.

## Work Completed

- Removed the unused checkbox field from `MainActivity`.
- Removed the unused checkbox field from `MainActivityWithAsyncTask`.
- Extended `scripts/check_android_contracts.py` to reject stale checkbox imports
  and `R.id.checkbox` references.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: source review showed `R.id.checkbox` references without a matching
  layout id.
- `python3 scripts/check_android_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

The Android build step is skipped in this environment because no Gradle wrapper
or root `settings.gradle` is checked in.

## Follow-Up Candidates

- Add a root Gradle wrapper/settings baseline so source compatibility can be
  verified on CI.
- Audit remaining fields for dead UI state that no longer maps to layout
  controls.
