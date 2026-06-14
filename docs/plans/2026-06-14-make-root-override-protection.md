# Make Root Override Protection

## Status: Planned

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

## Verification Plan

- Run focused static contracts and Make dry-run checks.
- Exercise all aliases from two working directories under hostile root
  assignments while preserving explicit Python and Gradle wrapper selection.
- Reject eight focused structural and evidence mutations.
- Run `make check` with an explicit timeout and the repository's pinned wrapper.
- Review the exact plan-scoped diff and audit generated artifacts, changed-line
  secrets, whitespace, and protected application/workflow/dependency paths.
