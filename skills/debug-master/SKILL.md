---
name: debug-master
description: Diagnose bugs, failing tests, runtime errors, and intermittent behavior by finding and verifying the root cause.
---

# Debug Master

## Investigation loop
1. **Capture the symptom.** Record expected versus actual behavior, exact error/output, environment, version, inputs, frequency, and user impact. Redact secrets from logs.
2. **Reproduce safely.** Find the smallest reliable reproduction. Preserve the failing state and avoid destructive commands or production changes.
3. **Build a timeline.** Inspect recent commits, configuration changes, dependency updates, logs, traces, and relevant code paths.
4. **Form hypotheses.** Rank plausible causes by evidence and cost to test. Choose the cheapest experiment that distinguishes between them.
5. **Instrument narrowly.** Add temporary diagnostics only where needed; avoid noisy logs and sensitive values. Remove temporary instrumentation before finishing.
6. **Fix the cause.** Make the smallest coherent change. Do not hide symptoms with broad exception handling, retries, sleeps, or weakened assertions.
7. **Prevent recurrence.** Add a regression test that fails before the fix and passes after it. Include boundary and failure behavior where relevant.
8. **Verify.** Rerun the reproduction, focused tests, and relevant broader checks. Inspect the final diff and check for collateral changes.

## Guardrails
- Change one causal factor at a time when practical.
- Distinguish correlation from causation; state when evidence is inconclusive.
- Check environment/configuration differences before blaming application logic.
- Do not delete user data, reset databases, rotate credentials, or change production state without explicit authorization.
- Never claim a fix is confirmed if the reproduction or regression test was not run.

## Final report
State the root cause (or remaining hypotheses), evidence, affected conditions, files changed, fix, regression coverage, exact commands/results, and any remaining risk.
