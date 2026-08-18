---
name: postgres-schema
description: Use when planning, implementing, reviewing, or troubleshooting ETL DAGs, SQL transformations, inserts, upserts, staging tables, source-to-target mappings, or PostgreSQL-dependent data pipelines.
---

# PostgreSQL Schema Inspection

Before writing or modifying ETL logic:

1. Identify all source, staging, mapping, and destination tables involved.
2. Use the `postgres_schema` tool to inspect each relevant table.
3. Never guess column names, column order, data types, nullability, default values, primary keys, unique constraints, foreign keys, partition columns, or conflict keys.
4. Build an explicit source-to-target mapping before implementation.
5. Verify insert and upsert columns against the retrieved schema.
6. Verify `ON CONFLICT` targets against real unique or primary-key constraints.
7. Report clearly when schema inspection fails.
8. Do not bypass project schema allowlists.
9. Do not request, expose, or store database credentials.
10. Do not connect to production unless the project configuration explicitly permits it.

The tool is for schema inspection only. It does not accept arbitrary SQL and should not be used as a database query runner.
