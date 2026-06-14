# Make Root Override Protection

## Status: Completed

## Context

The Makefile derives an absolute repository root so static and Android gates
work from any current directory. Its ordinary GNU Make assignment can still be
replaced by an environment or command-line `ROOT`, redirecting repository-owned
checker and Gradle working paths to another tree while a command appears to
verify this checkout.

Python and Gradle wrapper selection are intentionally configurable. Repository
ownership is not: every checked source and build path must remain anchored to
the checkout containing the invoked Makefile.

## Requirements

- Protect the derived repository root from environment and command-line
  reassignment.
- Preserve explicit `PYTHON` and `GRADLEW` overrides and all six public aliases.
- Prove repository and external working-directory invocations remain anchored
  under hostile root assignments.
- Add mutation-sensitive contracts for the declaration, assignment count and
  order, aliases, checker/Gradle paths, README index, and completed plan.
- Preserve Java, XML, Gradle, Android lifecycle, geocoding, workflow, and SDK
  behavior.

## Approach

Apply GNU Make's `override` directive only to the existing immediate root
assignment. Keep the protected root before configurable `PYTHON` and `GRADLEW`
declarations. Extend the canonical Android checker and use bounded dry-run
cases to exercise GNU Make precedence without bypassing native Android gates.

## Implementation Units

### Protect repository path ownership

- Update `Makefile` so exactly one protected root declaration owns repository
  paths.
- Retain the existing alias graph and both tool overrides.

### Add adversarial contracts

- Extend `scripts/check_android_contracts.py` with declaration-count, ordering,
  alias, checker/Gradle-path, README, and plan requirements.
- Run all six aliases from repository and external directories under hostile
  environment and command-line root assignments.
- Reject declaration, duplication, ordering, alias, path, documentation, and
  plan-state mutations.

### Record completed evidence

- Index this plan from `README.md`.
- Mark it completed only after focused, mutation, full static/Android, review,
  artifact, secret, and exact-diff validation succeeds.

## Risks And Mitigations

- Protecting tool variables would prevent supported SDK/test customization.
  Only `ROOT` becomes protected; `PYTHON ?=` and `GRADLEW ?=` stay unchanged and
  receive explicit override checks.
- A declaration-only assertion could miss a later reassignment or alias bypass.
  Count all assignments and require the alias graph plus repository-owned
  command paths.
- Local Android tooling may differ from hosted runners. Run the available full
  local gate and retain hosted Android as the exact-head native authority.

## Scope Boundaries

This change does not modify application logic, request lifecycle, geocoder
availability, typed receiver behavior, UI resources, SDK levels, dependency
versions, Gradle configuration, workflow policy, or deployment behavior.

## Work Completed

- Protected the derived repository root with GNU Make's `override` directive
  while preserving configurable Python and Gradle wrapper selection.
- Added declaration-count, ordering, alias, checker/Gradle-path, README, and
  plan contracts to the canonical Android checker.
- Indexed the completed evidence without changing Java, XML, Gradle,
  dependency, SDK, workflow, or application behavior.

## Verification Results

- All six public aliases passed dry-run verification from repository and
  external working directories under hostile environment and command-line
  `ROOT` assignments, for 24 bounded cases; explicit `PYTHON` and `GRADLEW`
  overrides remained effective.
- Eight declaration protection, duplicate assignment, ordering, alias,
  checker-path, README, missing-plan, and incomplete-plan mutations were
  rejected.
- The completed static gate passed seven grouped Android repository contracts
  from the repository and an external working directory.
- The pinned `make check` Gradle 8.14.5 gate reached Android project
  configuration under the shared Temurin 17 toolchain, then stopped because
  this host has no Android SDK location. Hosted Android test, assemble, and lint
  remain the native exact-head authority; no task or assertion was skipped or
  weakened.
- Plan-aware correctness, build-integrity, Android, testing, maintainability,
  reliability, and project-standards review found no actionable findings.
- Exact diff, protected Java/XML/Gradle/workflow/dependency path,
  generated-artifact, changed-line secret, and whitespace audits passed.
