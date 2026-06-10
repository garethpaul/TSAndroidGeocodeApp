# Reproducible Android Build

Status: Completed

## Problem

The sample targeted Android API 22 with an obsolete support library and had no
root Gradle project or wrapper. `make build` therefore skipped compilation, the
only test was an obsolete instrumentation placeholder, and modern Android
manifest, privacy, and dependency requirements were not validated.

## Plan

1. Restore a pinned JDK 17, Gradle, Android Gradle Plugin, and API 35 build.
2. Migrate the UI dependency from the retired support library to AndroidX.
3. Extract pure address and coordinate validation and cover boundary and
   malformed values with JVM unit tests.
4. Remove the undeclared AsyncTask alternative and resolve Android lint warnings
   rather than suppressing them.
5. Make static contracts, tests, assembly, and warnings-as-errors lint one local
   and hosted verification command.
6. Verify the wrapper distribution checksum and group dependency update noise.

## Verification

- `make check`
- Five `GeocodeInputValidatorTest` tests passed
- Debug APK assembled successfully against API 35
- Android lint passed with warnings treated as errors
- `git diff --check`
