## Context
Portfolio project transitioning from frontend-only to full-stack. Need secure GitHub integration, async bulk operations, and scalable deployment. Constraints: Follow project conventions (TypeScript, Vite, hooks, Django patterns), no production reqs yet.

## Goals / Non-Goals
- Goals: Enable bulk PR creation with global branches, editable metadata, user-accessible repos.
- Non-Goals: Advanced permissions (e.g., org-specific), multi-branch strategies, real-time UI updates.

## Decisions
- Backend: Django + DRF for APIs, Celery for tasks (standard for async; Django Tasks framework considered but Celery proven for workers).
- Frontend: Separate React SPA (simpler than embedded; Vite for build to match project conventions).
- Auth: django-allauth for GitHub OAuth (handles tokens securely).
- DB: PostgreSQL everywhere (via docker-compose locally, CloudSQL on GCP).
- Deployment: GCP Cloud Run (serverless, fits portfolio) with Terraform for infra.
- Alternatives: Embedded React (too complex), Firebase Auth (not GitHub-specific), SQLite (not prod-ready).

## Risks / Trade-offs
- Risk: GitHub API rate limits → Mitigation: Queue jobs, add delays.
- Trade-off: Global branches (simple) vs per-repo (more flexible but complex UI).
- Risk: Token security → Mitigation: Secure storage, no logs.

## Migration Plan
No existing data; start fresh. Rollback: Revert commits if issues.

## Open Questions
- Django Tasks vs Celery? (Proceeding with Celery for reliability.)
- GCP region? (Default to us-central1.)