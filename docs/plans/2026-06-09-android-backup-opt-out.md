# Android Backup Opt Out

Status: Completed
Date: 2026-06-09

## Goal

Keep the geocoding sample from backing up user-entered address or coordinate
state by default.

## Context

The sample processes user-entered addresses and coordinates before geocoder
work starts. That data can be personal, so the checked-in manifest should fail
closed and avoid platform app-data backup unless a maintainer deliberately
changes that boundary.

## Changes

- Set `android:allowBackup="false"` in `app/src/main/AndroidManifest.xml`.
- Extended `scripts/check_android_contracts.py` to require the manifest
  opt-out through parsed XML.
- Documented the privacy guard in README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 scripts/check_android_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
