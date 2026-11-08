---
name: database-architect
description: Design, review, or migrate relational and document data models with safe integrity, performance, and recovery properties.
---

# Database Architect

## Workflow
1. Inspect the existing schema, migrations, query patterns, ORM/driver, database engine/version, deployment topology, and backup/restore process.
2. Define entities, ownership, cardinality, lifecycle, retention, consistency needs, expected data volume, and access patterns before choosing a schema.
3. Encode invariants in the database where practical: primary/foreign keys, uniqueness, nullability, checks, and appropriate delete/update behavior.
4. Design indexes from actual query predicates, joins, ordering, and selectivity. Consider write amplification and storage cost; avoid speculative indexes.
5. Use parameterized queries. Define transaction boundaries and isolation expectations. Consider concurrent writers, retries, idempotency, lock contention, and deadlocks.
6. For migrations, prefer expand-migrate-contract: add compatible structures, backfill in bounded batches, deploy compatible code, verify, then remove obsolete structures in a later safe step.
7. Define rollback or forward-repair strategy, backup requirements, restore testing, and data validation.
8. Verify with representative queries, migration tests, constraints, and realistic concurrency/performance checks where feasible.

## Security and reliability
- Never store plaintext passwords, API keys, or tokens. Use established password hashing or a secret manager appropriate to the data.
- Apply least-privilege database credentials and separate runtime permissions from migration permissions.
- Minimize sensitive data; define retention and deletion behavior.
- Do not log raw credentials or sensitive records.
- Treat imported data and user-controlled query values as untrusted.
- Avoid destructive migrations without explicit approval and a verified recovery path.

## Deliverable
Document the schema and invariants, query/index rationale, migration sequence, compatibility window, operational risks, recovery plan, and exact validation performed. Clearly label unverified performance assumptions.
