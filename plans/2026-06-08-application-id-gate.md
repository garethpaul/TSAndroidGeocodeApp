# Application ID Gate

## Problem

The manifest and Java sources use `com.sample.foo.tsgeocodeapp`, but
`app/build.gradle` still declared `com.sample.foo.simplegeocodeapp`. That drift
can produce a differently identified Android app than the checked-in package
and manifest imply.

## TDD Evidence

1. Extended `scripts/check_android_contracts.py` with a Gradle application-id
   contract.
2. Ran `make lint` before changing Gradle and confirmed the new check failed
   on the package mismatch.
3. Aligned `applicationId` with the manifest package and reran the full
   verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
