# Geocode Result Coordinate Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Settle malformed successful geocoder callbacks safely instead of throwing on missing `Address` coordinates or displaying invalid coordinate values.

**Architecture:** Keep Android `Address` access inside the existing ViewModel receiver boundary, but verify `hasLatitude()` and `hasLongitude()` before calling their throwing getters. Reuse the pure `GeocodeInputValidator` range check when accepting successful callback values, with JVM tests for behavior and mutation-sensitive static contracts for the Android API access order.

**Tech Stack:** Java Android `Address`/`ResultReceiver`, AndroidX ViewModel/LiveData, JUnit 4, Python `unittest`, repository static contracts.

---

## Status: Completed

## Evidence And Decision

- `GeocodeViewModel.handleGeocodeResult(...)` currently calls `Address.getLatitude()` and `Address.getLongitude()` whenever a success bundle contains a non-null address.
- Android documents that each getter throws `IllegalStateException` when that coordinate has not been assigned, and provides `hasLatitude()` and `hasLongitude()` guards for this case.
- `GeocodeViewModel.completeResult(...)` accepts any non-null doubles, even though the existing input validator already defines the app's finite geographic coordinate boundary.
- Catching `IllegalStateException` would avoid the crash but would hide the explicit platform precondition and still allow non-finite or out-of-range callback values.
- Adding Robolectric would permit direct `Address` behavior tests but introduces an unnecessary dependency for a small guard whose integration can be protected by the existing mutation-sensitive source-contract suite.
- The selected approach is the smallest complete repair: explicit presence checks before getters, pure range validation before success publication, JVM regression tests, and static guard-order mutations.

### Task 1: Add failing callback validation tests

**Files:**
- Modify: `app/src/test/java/com/sample/foo/tsgeocodeapp/GeocodeViewModelTest.java`

**Step 1: Write the failing tests**

Add table-style cases that call `completeResult(...)` with `NaN`, infinities,
and values beyond latitude/longitude limits, then require the safe
`NO_GEOCODE_RESULT` fallback and a settled request.

**Step 2: Run tests to verify they fail**

Run: `./gradlew --no-daemon testDebugUnitTest --tests com.sample.foo.tsgeocodeapp.GeocodeViewModelTest`

Expected: FAIL because malformed successful coordinates are currently rendered.

### Task 2: Add failing Address presence contract

**Files:**
- Modify: `scripts/check_android_contracts.py`
- Modify: `tests/test_check_android_contracts.py`

**Step 1: Write the failing contract**

Require the successful `Address` branch to check both `hasLatitude()` and
`hasLongitude()` before either coordinate getter. Add hostile mutations that
remove either check or move the presence guard after a getter.

**Step 2: Run the focused contract to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_android_contracts.GeocodeResultCoordinateContractTest -v`

Expected: FAIL because the ViewModel currently reads both coordinates without
checking whether they are assigned.

### Task 3: Implement minimal callback guards

**Files:**
- Modify: `app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeViewModel.java`

**Step 1: Guard Android Address access**

Treat a null address or an address missing either coordinate as a malformed
success payload before calling `getLatitude()` or `getLongitude()`.

**Step 2: Reuse coordinate validation**

Require `GeocodeInputValidator.isCoordinateInRange(latitude, longitude)` in
`completeResult(...)` before publishing a successful display state.

**Step 3: Run focused tests**

Run the focused JUnit and Python contract commands from Tasks 1 and 2.

Expected: PASS.

### Task 4: Document and validate the boundary

**Files:**
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-25-geocode-result-coordinate-validation.md`

**Step 1: Document response integrity**

Record that successful geocoder callbacks require assigned, finite,
in-range latitude and longitude values before display.

**Step 2: Run repository validation**

Run: `make static`

Run when the Android SDK is available: `make check`

Expected: all portable contracts pass locally and the complete Android gate
passes in hosted CI.

**Step 3: Commit**

```bash
git add app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeViewModel.java \
  app/src/test/java/com/sample/foo/tsgeocodeapp/GeocodeViewModelTest.java \
  scripts/check_android_contracts.py tests/test_check_android_contracts.py \
  README.md SECURITY.md VISION.md CHANGES.md \
  docs/plans/2026-06-25-geocode-result-coordinate-validation.md
git commit -m "fix: validate geocode result coordinates"
```

## Validation Evidence

- The focused Python contract failed against the original ViewModel because
  successful result handling had no `Address` coordinate presence guard.
- The focused contract and all six hostile mutations passed after the
  presence, fallback, return, and range guards were added.
- `make static` passed all 28 Python tests and eight repository contracts.
- `make check` passed static checks and dependency resolution, then stopped
  before JVM tests because this local environment has no Android SDK
  configured. The hosted pull-request job remains the complete gate.
