# Kotlin Dependabot Compatibility Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Stop Dependabot from proposing Kotlin BOM versions that the reviewed AGP toolchain cannot build.

**Architecture:** Extend the canonical Gradle Dependabot ignore policy with the Kotlin 2.3 boundary enforced by the build compatibility matrix. Preserve Kotlin 2.2 patch eligibility and require the exact ignore range through mutation-sensitive static contracts.

**Tech Stack:** Dependabot YAML, Python `unittest`, Android Gradle Plugin 8.10.1

Status: Completed

---

### Task 1: Specify the Kotlin Ignore Boundary

**Files:**
- Modify: `tests/test_check_android_contracts.py`

**Step 1: Write the failing test**

Extend `VALID_DEPENDABOT` with an ignore for
`org.jetbrains.kotlin:kotlin-bom` versions `[2.3.0,)`, then add mutations for a
missing boundary, an overbroad 2.2 boundary, and a 2.4-only boundary that still
permits incompatible Kotlin 2.3 updates.

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_check_android_contracts.CheckDependabotContractsTest -v`

Expected: FAIL because `CANONICAL_DEPENDABOT` does not yet include the Kotlin
compatibility boundary.

### Task 2: Enforce the Canonical Policy

**Files:**
- Modify: `scripts/check_android_contracts.py`
- Modify: `.github/dependabot.yml`

**Step 1: Update the canonical policy**

Add the Kotlin BOM `[2.3.0,)` ignore with a comment tying removal to the AGP
8.13.2 migration.

**Step 2: Update the checked-in configuration**

Make `.github/dependabot.yml` match the canonical policy exactly.

**Step 3: Run the focused test**

Run: `python3 -m unittest tests.test_check_android_contracts.CheckDependabotContractsTest -v`

Expected: PASS.

### Task 3: Record and Validate the Cycle

**Files:**
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-24-kotlin-dependabot-compatibility.md`

**Step 1: Record the failed PR evidence**

Document that PR #22 proposed Kotlin 2.4.0 and failed the reviewed AGP matrix.

**Step 2: Run the repository gate**

Run: `make static`

Expected: PASS for all Python static contracts without requiring the Android
SDK or network dependency resolution.

Run `make check` as the final pull-request gate in the hosted Android
environment, where the reviewed SDK and JDK toolchain are provisioned.

**Step 3: Mark the plan complete**

Set `Status: Completed` after the focused test and `make static` pass.

Completed after the focused Dependabot contract suite and `make static` passed;
`make check` remains the required hosted pull-request gate.

Codex review identified that the initial `[2.4.0,)` boundary still allowed
Kotlin 2.3, which Android's compatibility table requires AGP 8.13.2 to process.
The test was tightened first, observed failing against the initial canonical
policy, and the implementation was corrected to `[2.3.0,)`.
