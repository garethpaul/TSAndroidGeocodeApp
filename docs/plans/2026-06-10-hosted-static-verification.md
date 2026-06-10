# Hosted Static Verification

Status: Completed

## Problem

The repository had a useful `make check` gate for source, manifest, resource,
and maintenance-plan contracts, but no hosted workflow ran it on pushes or
pull requests. The checked-in project also lacks a root Gradle wrapper and
`settings.gradle`, so CI must not imply that an Android APK was assembled.

## Plan

1. Add a least-privilege GitHub Actions workflow for the static repository
   gate on supported Python versions.
2. Pin third-party actions to immutable commit SHAs and bound job runtime.
3. Extend the local contract checker so workflow permissions, triggers,
   action pins, matrix, timeout, and command cannot silently drift.
4. Document that hosted verification covers static contracts while platform
   assembly still requires a compatible legacy Android toolchain.

## Verification

- `make check`
- `python3 -m py_compile scripts/check_android_contracts.py`
- Negative workflow-permission mutation rejected by `make lint`
- `git diff --check`
