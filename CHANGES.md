# Changes

## 2026-06-24 23:15 PDT - P2 - Block incompatible Kotlin Dependabot updates

### Summary

Confirmed that Dependabot PR #22 proposed Kotlin 2.4.0 against AGP 8.10.1,
which violates the repository's reviewed compatibility matrix, then encoded
that boundary in the canonical update policy.

### Work completed

- Ignored `org.jetbrains.kotlin:kotlin-bom` versions `[2.4.0,)` until the AGP
  9.1 migration.
- Preserved compatible Kotlin 2.2 patch updates.
- Added mutation-sensitive coverage for missing, overbroad, and exact-version
  Kotlin ignore policies.

### Threads

- None. The existing compatibility matrix, failing PR logs, and canonical
  Dependabot contract provided sufficient evidence for a direct TDD change.

### Files changed

- `.github/dependabot.yml` — added the Kotlin compatibility ignore range.
- `scripts/check_android_contracts.py` — updated the canonical Dependabot
  policy.
- `tests/test_check_android_contracts.py` — enforced the exact Kotlin boundary.
- `docs/plans/2026-06-24-kotlin-dependabot-compatibility.md` — recorded the
  implementation and validation plan.

### Validation

- Focused Dependabot contract test — failed before the canonical policy update.
- `python3 -m unittest tests.test_check_android_contracts.CheckDependabotContractsTest -v` — passed.
- `make static` — passed all static contract tests.

### Bugs / findings

- Dependabot grouping allowed a Kotlin minor update that requires AGP 9.1.0,
  while the repository intentionally remains on AGP 8.10.1.

### Blockers

- The nested Codex CLI identity remains unauthenticated, so the required Codex
  review gate cannot complete before merge.

### Next action

- Close incompatible PR #22, push this policy change to a new PR, and rerun
  Codex review after authenticating the nested CLI.

## 2026-06-17

- Retained one in-flight geocode request and its latest safe result across
  Activity configuration recreation with an Activity-scoped ViewModel.
- Moved the main-thread result receiver out of `MainActivity`; retained state
  uses a weak ViewModel reference and never stores an Activity, View, or Context.
- Added lifecycle-aware UI rendering and fifteen total JVM tests covering input
  validation plus retained request success, failure, fallback, and rollback.
- Pinned AndroidX Lifecycle 2.9.4 to preserve the API 21 device floor; Lifecycle
  2.10 and newer require API 23.

## 2026-06-13

- Disabled duplicate action-button dispatch while a geocoder request is active
  and restored interaction for every delivered result.
- Added activity and service guards that fail with localized feedback when
  Android reports no platform geocoder backend.
- Replaced the deprecated untyped parcelable receiver read with AndroidX's
  typed `IntentCompat` API while preserving the missing-receiver guard.

## 2026-06-12

- Removed user-entered coordinates and resolved street-address lines from
  Logcat while preserving generic diagnostics and visible results.

## 2026-06-10

- Derived each geocode request mode from the checked radio button so activity
  recreation cannot reset behavior while preserving a different visible mode.
- Replaced the Activity-retaining result receiver with a static receiver that
  uses a weak Activity reference, main-looper delivery, and lifecycle guards.
- Made every Make target independent of the caller's working directory.
- Fixed GitHub Actions jobs to Ubuntu 24.04, documented immutable action
  versions, and scoped concurrency to the workflow and ref.
- Extended static contracts with lifecycle, runner, action-version, and
  root-independent command mutation coverage.
- Restored a reproducible Android build with Gradle 8.14.5, Android Gradle
  Plugin 8.10.1, Android SDK 36, JDK 17, and AndroidX AppCompat 1.7.1.
- Raised the supported device floor from API 15 to API 21, matching current
  AppCompat requirements, and added Android 12+ backup/transfer exclusions.
- Extracted shared finite-coordinate and address normalization logic and added
  five JVM unit tests for null, whitespace, geographic boundaries, out-of-range
  values, `NaN`, and infinity.
- Removed the undeclared deprecated AsyncTask activity and replaced XML click
  reflection with explicit listeners in the active activity.
- Enabled Android lint warnings-as-errors and resolved the existing warning set.
- Added least-privilege GitHub Actions verification on Python 3.10/3.12 and a
  full JDK 17 Android test, assembly, and lint job with immutable action pins.
- Added a manual workflow trigger for maintenance verification.
- Disabled persisted checkout credentials in both hosted jobs and made the
  contract reject extra workflows, privileged triggers, write permissions, and
  duplicate action steps.
- Verified the Gradle distribution by checksum, installed exact Android SDK
  packages in CI, and added grouped weekly Gradle and Actions updates.
- Extended static contracts to enforce the modern toolchain, tests, workflow,
  privacy rules, and shared `make check` command.

## 2026-06-09

- Removed stale checkbox references from both activities and added static
  contract coverage against undeclared layout widget ids.
- Disabled app-data backup in the checked-in manifest and added static Android
  contract coverage for the opt-out.
- Fixed service and legacy AsyncTask address-line loops so the final geocoder
  line is included in rendered results.
- Extended static Android contract checks to require inclusive address-line
  result iteration.
- Guarded primary activity geocode result rendering against missing bundles,
  addresses, and result text.
- Extended static Android contract checks to require result payload guards.
- Added an IntentService `ResultReceiver` guard before geocoder work starts and
  extended static Android contract checks to require it.
- Added IntentService coordinate range validation before direct geocoder calls.
- Extended static Android contract checks to require service-side range guards.
- Added service-side address-name extra normalization before geocoder work.
- Extended static Android contract checks to require the IntentService to
  reject blank address-name extras.
- Added latitude/longitude range validation before service or AsyncTask geocoder
  work starts.
- Extended static Android contract checks to require coordinate range guards.
- Trimmed primary activity address-name input before validation so
  whitespace-only geocode requests do not start service work.

## 2026-06-08

- Guarded the legacy AsyncTask geocode path so invalid coordinates show
  feedback before background geocoder work starts.
- Added `make check` as the shared repository verification alias.
- Aligned the Gradle `applicationId` with the manifest and Java package.
- Extended static Android contract checks to catch future application-id drift.
- Added a `make verify` quality gate backed by static Android source and XML contract checks.
- Guarded latitude and longitude parsing so non-numeric input shows a validation message instead of crashing the app.
- Updated README and vision notes to reflect the checked-in Android source and legacy build shape.
- Added canonical `docs/plans` coverage and made the Android contract checker
  require completed plans.
