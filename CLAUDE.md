
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pull Request Helper is a full-stack web application for bulk pull request creation across multiple GitHub repositories. It uses a React frontend with TypeScript, Django REST Framework backend, PostgreSQL database, Celery for async task processing, and Redis as the message broker.

## Development Commands

### Frontend (React + Vite)

All commands should be run from the `frontend/` directory:

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Build and copy to backend static folder
npm run build:backend

# Run ESLint
npm run lint

# Run tests with Vitest
npm run test

# Run single test file
npm run test src/components/Form.test.tsx

# Run tests in watch mode
npm run test -- --watch
```

### Backend (Django)

All commands should be run from the `backend/` directory with virtual environment activated:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Django development server
python manage.py runserver

# Run database migrations
python manage.py migrate

# Run Django tests
python manage.py test

# Run Black formatter
black .

# Run Black check
black --check .
```

### Celery Worker

```bash
# From backend/ directory with venv activated
celery -A pr_helper worker --loglevel=info
```

### Docker Compose (Local Development)

```bash
# Start PostgreSQL and Redis services
docker-compose up -d db redis

# Stop services
docker-compose down
```

### OpenSpec CLI

This project uses OpenSpec for spec-driven development:

```bash
# List active changes
openspec list

# List specifications
openspec list --specs

# Show change details
openspec show <change-id>

# Validate a change
openspec validate <change-id> --strict

# Archive a completed change
openspec archive <change-id> --yes
```

## High-Level Architecture

### Frontend Architecture

- **Build Tool**: Vite with React plugin
- **Entry Point**: `frontend/src/main.tsx` → renders `App.tsx`
- **Components**: Located in `frontend/src/components/`
  - `Form.tsx` - Bulk PR creation form
  - `RepoList.tsx` - Repository selection component
  - `Login.tsx` - GitHub OAuth login button
- **Testing**: Vitest with Testing Library and jsdom environment
- **Static Assets**: Built files are copied to `backend/static/` and `backend/templates/`

### Backend Architecture

- **WSGI Application**: `pr_helper.wsgi:application`
- **URL Routing**: `pr_helper/urls.py` - includes auth URLs, API URLs, and serves frontend
- **API Endpoints** (`bulk_pr/urls.py`):
  - `GET /api/repos/` - List user's GitHub repositories
  - `POST /api/jobs/` - Create bulk PR job
  - `GET /api/csrf/` - Get CSRF token
  - `POST /api/logout/` - Delete OAuth token
  - `GET /health/` - Health check
  - `GET /health/ready/` - Readiness check with DB validation
- **Models** (`bulk_pr/models.py`):
  - `PRJob` - Stores bulk PR job data with repos, branches, title, body, status, results
- **Tasks** (`bulk_pr/tasks.py`):
  - `create_bulk_prs` - Celery task that processes PR creation asynchronously using PyGithub
- **Authentication**: Django Allauth with GitHub OAuth provider, storing tokens in `SocialToken` model

### Database Configuration

Settings in `pr_helper/settings.py` include two connection modes:

1. **Local Development**: Standard PostgreSQL connection via environment variables (`DB_HOST`, `DB_PORT`, etc.)
2. **Cloud SQL (Production)**: Uses Cloud SQL Python Connector when `USE_CLOUD_SQL_CONNECTOR=True`

Required environment variables: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

### Deployment Architecture

- **Platform**: Google Cloud Run via Terraform
- **CI/CD**: GitHub Actions (`.github/workflows/deploy.yml`)
- **Container Images**:
  - Web service: `gcr.io/PROJECT/pr-helper-web`
  - Worker service: `gcr.io/PROJECT/pr-helper-worker` (separate Dockerfile: `backend/Dockerfile.celery`)
- **Infrastructure**:
  - Cloud SQL PostgreSQL with private IP via VPC connector
  - Cloud Run services for web and worker
  - Redis (Cloud Memorystore or external)
  - Secret Manager for credentials
- **Optional Tailscale**: Set `TAILSCALE_ENABLED=true` and `TAILSCALE_AUTH_KEY` for private networking

### OpenSpec Change Management

The project uses a spec-driven development workflow defined in `openspec/`:

- `openspec/project.md` - Project conventions and guidelines
- `openspec/specs/` - Current specifications for capabilities (auth, bulk-pr-api, frontend-ui, task-processing)
- `openspec/changes/` - Active change proposals with `proposal.md`, `tasks.md`, and spec deltas
- `openspec/changes/archive/` - Completed changes

When planning new features or breaking changes, create a change proposal in `openspec/changes/<change-id>/` with:
1. `proposal.md` - Why, what changes, impact
2. `tasks.md` - Implementation checklist
3. `specs/<capability>/spec.md` - Delta specs with ADDED/MODIFIED/REMOVED requirements

### Key Files for Common Tasks

- **Add API endpoint**: Edit `backend/bulk_pr/views.py`, add URL in `backend/bulk_pr/urls.py`
- **Add frontend component**: Create in `frontend/src/components/`, import in `frontend/src/App.tsx`
- **Add database model**: Edit `backend/bulk_pr/models.py`, create migration, run `python manage.py migrate`
- **Add Celery task**: Edit `backend/bulk_pr/tasks.py`, import and call from views
- **Environment variables**: Set in `.env` file for local dev, GitHub Secrets for CI/CD, GCP Secret Manager for production
