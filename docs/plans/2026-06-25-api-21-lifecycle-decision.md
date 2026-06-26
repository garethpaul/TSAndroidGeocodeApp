# API 21 And AndroidX Lifecycle Decision

Status: Completed

## Problem

The sample supports API 21 and uses AndroidX Lifecycle 2.9.4 for retained
request/result state. AndroidX Lifecycle 2.10.0 raised its minimum SDK from API
21 to API 23, leaving the roadmap to decide whether dependency updates should
silently drop API 21 and 22.

## Decision

- Retain `minSdk = 21` and AndroidX Lifecycle 2.9.4.
- Keep Dependabot ignoring Lifecycle 2.10.0 and newer while the API 21 floor is
  intentional.
- Do not raise the platform floor solely to accept a dependency update.
- Reconsider API 23 only in a dedicated IntentService and geocoder migration
  that includes emulator coverage for activity/service result delivery.

## Evidence

- `app/build.gradle` declares API 21 and pins both Lifecycle artifacts to 2.9.4.
- `.github/dependabot.yml` already prevents incompatible Lifecycle updates.
- Android's official Lifecycle 2.10.0 release notes state that the minimum SDK
  changed from API 21 to API 23:
  https://developer.android.com/jetpack/androidx/releases/lifecycle#2.10.0

## Verification

- Observed `python3 scripts/check_android_contracts.py` fail on the missing
  decision plan before adding this record and synchronized documentation.
- `make static` passed 28 checker tests and all eight repository contracts.
- Local `make check` passed static checks and dependency resolution, then
  stopped because this host has no `ANDROID_HOME`; hosted SDK 36 verification
  remains the authoritative full Android gate.
- Three isolated hostile mutations were rejected: removing the README decision,
  restoring the completed roadmap question, and marking this plan incomplete.
- Hosted `make check` is required before merge.
- `git diff --check`
