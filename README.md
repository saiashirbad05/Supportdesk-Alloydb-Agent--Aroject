# Supportdesk AlloyDB Agent Project

A clean, organized reference project for deploying a support ticket query API on top of AlloyDB for PostgreSQL, with Cloud Run delivery and AlloyDB AI natural language integration.

## What This Repository Contains

- A production-style Flask API for querying a custom `supportdesk` dataset stored in AlloyDB
- Cloud Run deployment files
- A structured deployment guide based on the working commands and the errors encountered during setup
- Test scripts for validating the public service URL
- Archived raw reference files used during the project build-out

## Live Service

- Base URL: `https://supportdesk-nl-api-260584325793.us-central1.run.app`
- Root: `https://supportdesk-nl-api-260584325793.us-central1.run.app/`
- Health: `https://supportdesk-nl-api-260584325793.us-central1.run.app/health`
- Demo Payments Query: `https://supportdesk-nl-api-260584325793.us-central1.run.app/demo/payments-open`
- Demo Unresolved Query: `https://supportdesk-nl-api-260584325793.us-central1.run.app/demo/unresolved-by-service`
- Demo Critical Auth Query: `https://supportdesk-nl-api-260584325793.us-central1.run.app/demo/critical-auth`

## Project Structure

```text
supportdesk-alloydb-agent-project/
|-- app/
|   |-- app.py
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- .env.example
|-- docs/
|   |-- DEPLOYMENT_GUIDE.md
|   |-- LIVE_SERVICE_CHECKS.md
|   `-- reference/
|       |-- AlloyDB_AI_Complete_Guide.raw.txt
|       `-- service_sab.raw.txt
|-- scripts/
|   |-- test_endpoints.sh
|   `-- test_endpoints.ps1
|-- .gitignore
`-- README.md
```

## Key Features

- Custom support ticket dataset, not the default AlloyDB retail sample
- Cloud Run API backed by AlloyDB for PostgreSQL
- Fixed demo endpoints for reliable public testing
- Optional AlloyDB AI natural language endpoint
- Troubleshooting notes for the exact errors hit during setup:
  - public IP password flag validation
  - Auth Proxy SSL misuse
  - proxy connection refused
  - `psql -lqt` PostgreSQL 17 catalog mismatch
  - wrong NL flag name
  - extension ownership issue
  - Vertex AI model access errors

## Application Endpoints

### `GET /`

Returns service information and the available routes.

### `GET /health`

Health route used by the deployed service.

### `GET /healthz`

Compatibility alias for health checks.

### `GET /demo/payments-open`

Returns all open `High` or `Critical` tickets for the `payments` service created on or after `2026-03-01`.

### `GET /demo/unresolved-by-service`

Returns unresolved ticket counts grouped by service.

### `GET /demo/critical-auth`

Returns the engineer assigned to the open critical auth ticket.

### `POST /ask`

Attempts to convert a natural-language question into SQL using `alloydb_ai_nl.get_sql(...)`, then executes the generated SQL if it is a `SELECT`.

## Quick Local Notes

This repo is designed primarily as a Cloud Run deployment reference. If you run locally, you must provide:

- `INSTANCE_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASS`
- optional `NL_CONFIG_ID`

## Deployment Summary

1. Create the AlloyDB cluster and instance.
2. Load the `supportdesk` dataset.
3. Enable `alloydb_ai_nl.enabled=on`.
4. Deploy the Flask API to Cloud Run with Direct VPC egress.
5. Test the public endpoints.

## Notes on GitHub Push

This workspace includes a clean local project folder ready to push. If the remote GitHub repository does not already exist, create a repository named `supportdesk-alloydb-agent-project` under your account and then push this folder contents to it.
