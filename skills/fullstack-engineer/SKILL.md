---
name: fullstack-engineer
description: Build or change end-to-end product features across frontend, backend, APIs, authentication, and persistence.
---

# Fullstack Engineer

## Implementation workflow
1. Inspect project instructions, app structure, framework versions, scripts, tests, and existing UI/API/data patterns before editing.
2. Trace the full user journey: entry point, client state, network/API contract, authorization, validation, business logic, persistence, and response rendering.
3. Define acceptance criteria and edge cases. Preserve existing API and data compatibility unless a breaking change is explicitly requested.
4. Implement the smallest complete vertical slice. Reuse established components and patterns; avoid unnecessary dependencies and duplicated business rules.
5. Enforce trust boundaries on the server. Validate all untrusted input, authorize every protected operation, and never expose secrets or privileged data to the client.
6. Handle loading, success, empty, partial, offline, timeout, and error states where applicable. Make retries safe and avoid duplicate writes.
7. Add tests at the appropriate layers: unit, API/integration, and user-flow/component tests. Include invalid input, permissions, and failure paths.
8. Run formatting/linting, type checks, focused tests, full relevant test suites, and production builds when available. Inspect the final diff.

## Quality and security
- Keep accessibility, keyboard navigation, responsive behavior, and clear feedback in scope for UI changes.
- Avoid trusting client-side validation or hidden controls as authorization.
- Use parameterized database access and safe output encoding.
- Bound uploads, pagination, payload sizes, execution time, and other resource-intensive operations.
- Do not log credentials, session tokens, or sensitive request bodies.
- Do not silently change migrations, defaults, or destructive behavior.

## Completion report
Summarize user-visible behavior, key implementation choices, changed files, compatibility/migration impact, tests and exact results, and known limitations. Never say “done” for checks that were not run.
