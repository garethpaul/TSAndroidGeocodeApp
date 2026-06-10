# Hosted Verification

Status: Completed

## Problem

The repository had source, manifest, resource, and maintenance-plan contracts,
but no hosted workflow ran them on pushes or pull requests. The initial project
also lacked a complete root build, so neither local nor hosted verification
could compile the application.

## Plan

1. Add a least-privilege GitHub Actions workflow for the static repository gate
   on supported Python versions.
2. Pin third-party actions to immutable commit SHAs and bound job runtime.
3. Add a JDK 17 Android job that runs the same complete `make check` command as
   developers, including unit tests, APK assembly, and warnings-as-errors lint.
4. Extend the contract checker so permissions, triggers, action pins, matrices,
   timeouts, and commands cannot silently drift.

## Verification

- `make check`
- `python3 -m py_compile scripts/check_android_contracts.py`
- Negative workflow-permission mutation rejected by `make lint`
- `git diff --check`
