# Result Receiver Lifecycle Safety

Status: Completed

## Problem

The non-static `ResultReceiver` inner class implicitly retained `MainActivity`
while the `IntentService` performed geocoding. A delayed result could therefore
keep a destroyed Activity alive and update stale views after configuration
changes. Repository commands also assumed they were launched from the project
root, and hosted jobs used a floating Ubuntu runner label.

## Plan

1. Convert the receiver to a static class with a weak Activity reference.
2. Dispatch callbacks on the main looper and discard results for missing,
   finishing, or destroyed activities.
3. Keep payload interpretation in the Activity without retaining it from the
   background request.
4. Make all Make targets resolve paths from the Makefile location.
5. Pin hosted verification to Ubuntu 24.04 and retain immutable action SHAs
   with readable release annotations.
6. Extend static contracts and mutation checks to prevent these guarantees
   from silently regressing.

## Verification

- `make check`
- `make -f /path/to/TSAndroidGeocodeApp/Makefile static` from outside the repo
- Receiver strong-reference, non-static-class, lifecycle-guard, runner-label,
  and Makefile path mutations rejected by the static contract checker
- `git diff --check`
