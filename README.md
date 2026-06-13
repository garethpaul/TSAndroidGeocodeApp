# TSAndroidGeocodeApp

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`TSAndroidGeocodeApp` is a small Java Android sample that resolves either an
address name or a latitude/longitude pair through Android's `Geocoder`. The
activity validates input and delegates geocoding to an `IntentService`, which
returns the first result through a `ResultReceiver`.

The project is maintained as an educational sample. It is reproducibly
buildable, but it is not presented as a production geocoding client and has no
device-level test suite.

## Supported Toolchain

- JDK 17
- Android SDK Platform 36 and Build Tools 35.0.0
- Gradle 8.14.5 through the checked-in wrapper
- Android Gradle Plugin 8.10.1
- AndroidX AppCompat 1.7.1
- Android API 21 minimum and API 36 target

The API 21 floor is required by the current AndroidX AppCompat release.

## Setup

Install JDK 17 and Android SDK Platform 36, then point `ANDROID_HOME` at the
SDK. The Gradle wrapper downloads the pinned Gradle distribution.

```bash
git clone https://github.com/garethpaul/TSAndroidGeocodeApp.git
cd TSAndroidGeocodeApp
export JAVA_HOME=/path/to/jdk-17
export ANDROID_HOME=/path/to/android-sdk
make check
```

Open the repository root in Android Studio to run the debug application on an
API 21+ device or emulator. The application uses Android's platform geocoder,
so result availability and quality depend on the device implementation and
network conditions.

## Verification

- `make static` validates source, manifest, resource, build, workflow, and
  maintenance-plan contracts.
- `make test` runs the five JVM unit tests for address normalization and
  coordinate boundaries, including `NaN` and infinity rejection.
- `make build` assembles the debug APK.
- `make lint` runs static contracts and Android lint with warnings treated as
  errors.
- `make check` runs the complete unit-test, APK, lint, and contract gate.

GitHub Actions runs the static contracts on Python 3.10 and 3.12 and runs the
full Android gate on JDK 17 and Ubuntu 24.04 for pushes, pull requests, and
manual runs. Workflow permissions are read-only, checkout credentials are not
persisted, and action revisions are pinned to immutable commits. Repository
contracts reject extra workflows, privileged pull-request triggers, write
permissions, and duplicate action steps. The Gradle distribution is verified
by checksum, and Dependabot groups weekly Gradle and Actions updates.

## Behavioral Contracts

- Address names are trimmed and blank names are rejected before geocoding.
- Coordinates must be finite and inside latitude `[-90, 90]` and longitude
  `[-180, 180]` before a geocoder call.
- Direct service requests without a `ResultReceiver` are rejected.
- Service requests read the receiver through AndroidX's typed parcelable compat
  API across the supported API 21-36 range.
- Missing or malformed result payloads do not crash UI rendering.
- Background results use a main-looper receiver with a weak Activity reference,
  and results are discarded after the Activity starts finishing or is destroyed.
- Fetch requests derive their mode from the checked radio button, keeping
  restored UI state aligned with the request after Activity recreation.
- Every address line reported by Android is included in the rendered result.
- User-entered coordinates and resolved address lines are not copied into
  Logcat; the service retains generic failure diagnostics only. See
  `docs/plans/2026-06-12-geocode-log-privacy.md`.
- App data is excluded from legacy backup, cloud backup, and device transfer.

## Limitations

- Android's `IntentService` and synchronous `Geocoder` APIs used by this
  historical sample are deprecated on newer Android releases.
- Unit tests cover pure input validation; geocoder behavior and result delivery
  across Activity recreation still require device or emulator verification.
- The sample does not request device location, persist addresses, or include
  API keys.

## Repository Guide

- `app/src/main` contains the activity, service, validator, manifest, and UI.
- `app/src/test` contains dependency-free JVM validation tests.
- `scripts/check_android_contracts.py` enforces repository-level contracts.
- `docs/plans` records completed maintenance changes and their validation.
- `CHANGES.md`, `SECURITY.md`, and `VISION.md` describe maintenance history,
  disclosure guidance, and project scope.

## Contributing

Keep changes focused on the sample's existing geocoding flow. Do not commit API
keys or real user location data. Run `make check` before opening a pull request
and update documentation when supported SDK or build requirements change.
