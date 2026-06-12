# Changes

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
