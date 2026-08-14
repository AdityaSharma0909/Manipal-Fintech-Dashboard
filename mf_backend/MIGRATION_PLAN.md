# Revamp / Migration Plan

This project is not yet in production. The goal is to keep all current functionality while restructuring for extensibility, cleaner architecture, and safer operations. The plan below is incremental and contract-safe for existing endpoints.

## Objectives
- Preserve current behaviors and response shapes while internal refactors happen.
- Introduce clear layering (domain/use-case/adapters) and reusable services.
- Replace hardcoded choices with ref-data tables.
- Normalize integrations (KYC/OTP/storage/esign) behind adapters.
- Improve observability and security defaults.
- Add a regression test baseline before deeper changes.

## Current Surface (must remain)
- Auth/OTP flows: staff/customer/agent/lead; agent OTP endpoints.
- Leads: legacy + `new-lead` flows; dashboards.
- Accounts: legacy + `new-account`.
- Applications: legacy + `new-application`.
- KYC/verification: PAN/Aadhaar/bank via FRS/Sprint/Zoop; Zoop PAN/bank/OCR-lite/DL/Voter/Passport.
- Documents/uploads across lead/account/application; bank documents.
- Gold price/calculators; lender/product endpoints.
- Agent account/bank account flows.
- Pincode lookup.
- Leegality eSign.

## Phase 0 – Baseline & CI Guardrails
- Export current API contracts (OpenAPI/manual) for the endpoints listed above.
- Add smoke tests (pytest) for: agent OTP, user/customer OTP, lead OTP, `new-lead`/`new-account`/`new-application`, `account/verify` (PAN/bank), Zoop PAN/bank/OCR-lite, Leegality template-sign/status, pincode, gold price/calculators, agent account/bank account.
- Add CI steps: ruff (lint), black (format), mypy (informational), pytest (smoke).

## Phase 1 – Config & Logging
- Move secrets/keys to env; remove hardcoded `SECRET_KEY`, keep DEBUG/ALLOWED_HOSTS/CORS env-driven (permissive only in dev).
- Enable structured logging (JSON) with request/user IDs; remove prints.
- Add error-handling middleware that maps exceptions to the existing HttpResponse envelope (no shape change).

## Phase 2 – Refdata (additive)
- Create refdata tables with admin/CRUD: document types/subtypes, sources, loan/product categories/subcategories, banks/branches (geo/map link), nominee relations, etc.
- Seed fixtures; keep legacy choice enums for v1; map them to refdata internally.

## Phase 3 – Adapters
- KYC adapter interface (FRS/Sprint/Zoop) with normalized responses; route `account/verify` and Zoop views through it.
- OTP service wrapper for all OTP endpoints (staff/customer/agent/lead/application).
- Storage wrapper for MinIO/S3 (signed URLs, consistent prefixes).
- Esign adapter (Leegality) with normalized responses.

## Phase 4 – Documents
- Add metadata JSONB and type/subtype FK/status (additive) to Document.
- Introduce a document service (upload/list/status) using the storage wrapper.
- Refactor lead document flow to the service first; then account/application; keep payloads unchanged.

## Phase 5 – KYC Logging & Policies
- Add a KYC verification log table (type, vendor, status, payload/meta, related entity).
- Centralize business rules (PAN uniqueness, bank doc prerequisites, status transitions) in services; views call services.
- Add idempotency keys for sensitive POSTs where feasible (no contract change needed if optional).

## Phase 6 – Lead/Account/Application Consolidation
- Keep legacy models; move logic into use-case services.
- Ensure `new-lead`/`new-account`/`new-application` flows reuse shared services for validation, ID generation, and status updates.

## Phase 7 – Agent Flows
- Ensure agent OTP uses OTP service; agent account/bank account uses document/storage service where relevant and refdata for banks/branches.

## Phase 8 – Observability & Metrics
- Request/response logging (PII redacted), latency/error metrics on key endpoints.
- Health/readiness endpoints.
- Optional tracing hooks (OTel) behind a flag.

## Phase 9 – Testing Expansion
- Unit tests for services/adapters.
- API tests for all v1 endpoints.
- Integration tests with docker-compose (Postgres, MinIO; Redis if introduced).
- Contract tests for external adapters (mocked Zoop/Leegality/KYC vendors).
- Gradually raise coverage thresholds.

## Phase 10 – Optional v2
- If cleaner APIs are desired, add `/v2` using refdata + unified services; keep `/v1` intact until all clients migrate.

## Rollout
- Develop in branches; run migrations in staging with dry-runs/checksums.
- Deploy dev → staging → prod; canary if possible.
- Monitor logs/metrics; rollback plan ready.

## Notes
- Favor additive migrations; avoid destructive DDL on legacy tables.
- Keep response shapes stable during refactors.
- Use feature flags where behavior could differ by tenant/client.
