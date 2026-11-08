---
name: test-engineer
description: Plan, write, and run unit, integration, regression, and end-to-end tests for software changes.
---

# Test Engineer

## Test design workflow
1. Read project test instructions, test configuration, fixtures, CI workflows, and nearby tests. Identify the actual framework and supported runtime.
2. Derive cases from observable requirements and state transitions, not implementation details alone. Map each acceptance criterion to at least one assertion.
3. Cover representative success paths, boundaries, malformed/untrusted input, permissions, missing resources, concurrency/retries, and dependency failures as relevant.
4. Choose the narrowest useful test level: unit for isolated logic, integration for boundaries/persistence, and end-to-end for critical user journeys.
5. Keep tests deterministic and isolated. Control time, randomness, network, filesystem, and external services with explicit fixtures or fakes. Avoid unnecessary sleeps and order dependence.
6. Assert meaningful outcomes and side effects. Ensure a regression test fails for the original defect and passes with the fix.
7. Run focused tests first, then relevant suites and quality gates. Record exact commands, exit codes, counts, skips, and environmental blockers.
8. Review test quality: remove flaky assumptions, broad mocks that hide behavior, weak assertions, and fixtures that leak state.

## Guardrails
- Do not weaken or delete an existing assertion merely to get a green build without explaining and justifying the behavior change.
- Do not report unexecuted tests as passed. Distinguish failed tests from tests that could not run.
- Avoid tests that depend on production credentials, live user data, or uncontrolled external services.
- For security-sensitive behavior, test both allowed and denied paths.

## Deliverable
Provide a requirement-to-test summary, files added/changed, exact commands and observed results, skipped coverage, and residual risks.
