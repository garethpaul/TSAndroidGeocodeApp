# Sparse Address Line Handling

Status: Completed

## Problem

Android documents that `Address.getAddressLine(index)` may return `null`, while
`getMaxAddressLineIndex()` reports only the largest index in use. Joining every
slot verbatim could therefore render the literal text `null`, preserve
whitespace-only lines, or deliver a successful result with no usable address
text.

## Scope

- Keep iterating through the final reported address-line index.
- Trim usable address lines and skip null or blank entries.
- Preserve the original line order and platform line separator.
- Deliver `Not Found` as a failure when no usable line remains.
- Keep coordinates and resolved address text out of Logcat.

## Work Completed

- Added a pure-Java address-line formatter beside the existing input validator.
- Routed service result formatting through the tested helper.
- Added sparse/missing and all-empty JVM regressions.
- Added mutation-sensitive checker coverage and synchronized guidance.

## Verification Completed

- RED direct `javac` probe failed because the formatter contract was absent.
- GREEN direct `javac` probe passed for sparse and all-empty line sets.
- Twenty-nine portable checker tests and all eight static Android contracts
  passed locally.
- Nine isolated hostile source, regression, guidance, and plan mutations were
  rejected.
- `git diff --check` passed.
- Full Android SDK verification remains hosted because no local Android SDK is
  configured in this environment.
- Hosted `make check` is required before merge.

## Residual Risk

Actual line content and ordering remain provider-specific. Device/emulator
verification across platform geocoder implementations remains the integration
gate for rendered output.
