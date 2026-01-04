# Change: Add Bulk Pull Request Creation

## Why
The project lacks core functionality for bulk PR creation, which is the portfolio's main purpose. Users need a way to authenticate with GitHub, select repositories, specify branches globally, and submit jobs for automated PR creation to demonstrate modern web dev practices.

## What Changes
- Add GitHub OAuth authentication (backend + frontend).
- Implement backend APIs for listing repos and enqueueing PR jobs.
- Build React SPA with repo selection, branch inputs, and job submission UI.
- Add asynchronous task processing for bulk PR creation via GitHub API.
- Set up local PostgreSQL via Docker Compose and GCP Cloud Run deployment with Terraform.
- **BREAKING**: Shifts from frontend-only to full-stack app.

## Impact
- Affected specs: New capabilities (github-auth, bulk-pr-api, frontend-ui, task-processing).
- Affected code: New backend (Django), updated frontend (React), new deployment infra.
- No existing code modified; project conventions (TypeScript, hooks, etc.) followed.