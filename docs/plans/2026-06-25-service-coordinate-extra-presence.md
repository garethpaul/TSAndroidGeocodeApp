# Service Coordinate Extra Presence Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Reject direct location-mode service requests that omit either coordinate extra instead of silently geocoding the default `(0, 0)`.

**Architecture:** Keep validation at the existing `IntentService` trust boundary. Add a mutation-sensitive Python contract for paired `Intent.hasExtra(...)` checks, then guard both extras before reading doubles or calling the platform geocoder.

**Tech Stack:** Java Android `IntentService`, Python `unittest`, repository static contracts, Gradle/JUnit verification.

---

## Status: Completed

## Evidence And Decision

- `MainActivity` always supplies both coordinate extras for accepted UI requests.
- `GeocodeAddressIntentService` also accepts direct intents, but `getDoubleExtra(..., 0)` currently converts a missing latitude or longitude into a valid zero.
- The existing address-mode branch rejects a missing name, so coordinate mode should enforce the same service-boundary completeness.
- A typed request parser would improve structure but is unnecessary for this two-field invariant; paired presence checks are the smallest reversible fix.

### Task 1: Add the failing contract

**Files:**
- Modify: `tests/test_check_android_contracts.py`
- Modify: `scripts/check_android_contracts.py`

**Step 1: Write the failing test**

Add a source-contract helper test that accepts the current service text only when it contains both:

```java
intent.hasExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA)
intent.hasExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA)
```

The contract must also require the combined missing-extra guard to appear before both `getDoubleExtra(...)` calls and before `geocoder.getFromLocation(...)`. Add hostile mutations that remove either presence check or move the guard after coordinate reads.

**Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_android_contracts -v`

Expected: FAIL because the service has no coordinate-extra presence guard.

### Task 2: Reject incomplete coordinate payloads

**Files:**
- Modify: `app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeAddressIntentService.java`

**Step 1: Write minimal implementation**

Before reading either coordinate, reject when either extra is absent:

```java
if(!intent.hasExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA)
        || !intent.hasExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA)) {
    errorMessage = "Invalid Latitude or Longitude Used";
    Log.e(TAG, errorMessage);
} else {
    double latitude = intent.getDoubleExtra(...);
    double longitude = intent.getDoubleExtra(...);
    // existing range validation and geocoder lookup
}
```

**Step 2: Run tests to verify they pass**

Run: `make static`

Expected: PASS, including hostile source mutations.

### Task 3: Document and fully validate

**Files:**
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-25-service-coordinate-extra-presence.md`

**Step 1: Record the boundary**

Document that direct location-mode service calls require both coordinate extras and that missing payload fields never fall back to zero.

**Step 2: Run repository validation**

Run: `make static`

Run when Android SDK/JDK are available: `make check`

Expected: all portable contracts, JVM tests, Android lint, and debug assembly pass.

## Validation Evidence

- The focused service coordinate payload contract failed against the original
  source because no paired `Intent.hasExtra(...)` guard existed.
- The focused contract and its three hostile mutations passed after the service
  rejected incomplete location payloads before coordinate reads.
- `make static` and `make check` are the required final verification commands.

**Step 3: Commit**

```bash
git add app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeAddressIntentService.java \
  tests/test_check_android_contracts.py scripts/check_android_contracts.py \
  README.md SECURITY.md VISION.md CHANGES.md \
  docs/plans/2026-06-25-service-coordinate-extra-presence.md
git commit -m "fix: reject incomplete geocode coordinates"
```
