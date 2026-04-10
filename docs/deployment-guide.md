# Deployment Guide

## Local Stack

- Docker Compose file: `infra/docker-compose.yml`
- Services: Postgres, Redis, MinIO, API, Worker, Web

## Production Notes (AWS-oriented)

1. Compute

- API + worker on ECS/Fargate or Kubernetes
- Web on Vercel, ECS, or containerized Node runtime

2. Data

- Postgres: Amazon RDS (enable pgvector extension)
- Object storage: Amazon S3
- Queue/cache: Amazon ElastiCache Redis

3. Secrets

- Use AWS Secrets Manager / SSM Parameter Store
- Do not store production secrets in `.env`

4. Observability

- OTLP-compatible telemetry sink
- central JSON log aggregation

5. Background jobs

- scale worker independently from API
- use dead-letter policies for failed job patterns

## Environment Separation

- separate dev/staging/prod configs
- distinct DB, bucket, and Redis namespaces per environment
