# Deployment Guide

## Overview

This project deploys a Flask API to Cloud Run and connects it to AlloyDB for PostgreSQL using a custom support ticket dataset.

## Core Setup Flow

1. Set project variables.
2. Enable APIs.
3. Create the AlloyDB cluster and primary instance.
4. Start the AlloyDB Auth Proxy from Cloud Shell for initial setup.
5. Create the `supportdesk` database and `app.support_tickets` table.
6. Insert the custom dataset.
7. Enable AlloyDB AI natural language.
8. Configure manual context and templates.
9. Deploy the Cloud Run API.
10. Verify the live routes.

## Commands Used

### Enable APIs

```bash
gcloud services enable \
  alloydb.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Create AlloyDB Instance with Public IP

```bash
gcloud alloydb instances create "${INSTANCE_ID}" \
  --instance-type=PRIMARY \
  --availability-type=ZONAL \
  --cpu-count=2 \
  --region="${REGION}" \
  --cluster="${CLUSTER_ID}" \
  --project="${PROJECT_ID}" \
  --assign-inbound-public-ip=ASSIGN_IPV4 \
  --database-flags=password.enforce_complexity=on
```

### Enable AI Natural Language

```bash
gcloud alloydb instances update "${INSTANCE_ID}" \
  --cluster="${CLUSTER_ID}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --database-flags=password.enforce_complexity=on,alloydb_ai_nl.enabled=on,google_ml_integration.enable_model_support=on
```

### Deploy Cloud Run

```bash
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --allow-unauthenticated \
  --network "${NETWORK}" \
  --subnet "${SUBNET}" \
  --vpc-egress private-ranges-only \
  --set-env-vars "DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PASS=${DB_PASSWORD},DB_PORT=5432,INSTANCE_HOST=${INSTANCE_HOST}" \
  --min-instances=1
```

## Errors Already Solved in This Project

- Public IP creation requires `password.enforce_complexity=on`
- Do not use `sslmode=require` with `alloydb-auth-proxy`
- Do not use `psql -lqt` on this PostgreSQL 17 environment
- Use `alloydb_ai_nl.enabled=on`, not `alloydb.ai_nl_enabled`
- Do not run `ALTER EXTENSION google_ml_integration UPDATE`
- If Vertex model access fails, use manual context and `check_intent => FALSE`
