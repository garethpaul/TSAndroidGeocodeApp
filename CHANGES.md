# Changes

## 2026-06-10

- Added least-privilege GitHub Actions verification on Python 3.10 and 3.12
  with immutable action pins and a bounded runtime.
- Extended static contracts to enforce workflow triggers, permissions, action
  provenance, matrix coverage, timeout, and the shared `make check` command.
- Documented that hosted verification covers static contracts while Android
  APK assembly still requires a compatible legacy toolchain.

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
