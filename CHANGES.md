# Changes

## 2026-06-08

- Aligned the Gradle `applicationId` with the manifest and Java package.
- Extended static Android contract checks to catch future application-id drift.
- Added a `make verify` quality gate backed by static Android source and XML contract checks.
- Guarded latitude and longitude parsing so non-numeric input shows a validation message instead of crashing the app.
- Updated README and vision notes to reflect the checked-in Android source and legacy build shape.
