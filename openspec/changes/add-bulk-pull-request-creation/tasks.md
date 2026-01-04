## 1. Project Setup and Authentication
- [x] 1.1 Set up Django project with DRF, allauth/dj-rest-auth for GitHub OAuth
- [x] 1.2 Configure PostgreSQL via docker-compose.yaml for local dev
- [x] 1.3 Install deps: Django 6.0+, Celery, psycopg2, corsheaders, whitenoise
- [x] 1.4 Create models: User (allauth), Job (repos, branches, title/body, status)
- [x] 1.5 Set up Celery for task processing

## 2. Backend API and Core Logic
- [x] 2.1 Implement /api/repos/ (GET user repos via GitHub API)
- [x] 2.2 Implement /api/jobs/ (POST to enqueue job)
- [x] 2.3 Add Celery task for bulk PR creation (loop repos, create PRs, handle errors)
- [x] 2.4 Add defaults: source 'main', title "<source> -> <destination>", body GitHub default
- [x] 2.5 Configure CORS for React dev proxy

## 3. React Frontend (SPA)
- [x] 3.1 Create React app with Vite in frontend/ folder (match project conventions)
- [ ] 3.2 Build Login component (OAuth redirect)
- [ ] 3.3 Build RepoList component (checkboxes, API fetch)
- [ ] 3.4 Build Form component (global source/dest inputs, editable title/body)
- [ ] 3.5 Build Submit component (API call, job status tracking)
- [ ] 3.6 Set up build/serving: npm run build, Django serves static files

## 4. Integration and Testing
- [ ] 4.1 Connect frontend to backend (auth tokens, API calls)
- [ ] 4.2 Test full flow: OAuth -> repos -> submit -> PR creation
- [ ] 4.3 Add tests: Django for API/tasks, Vitest for React
- [ ] 4.4 Handle edge cases: failures, permissions, rate limits

## 5. Polish and Deployment
- [ ] 5.1 Add UI polish: loading states, errors, progress indicators
- [ ] 5.2 Security: input validation, rate limiting
- [ ] 5.3 Set up Terraform for GCP Cloud Run + CloudSQL
- [ ] 5.4 Configure GitHub Actions for CI/CD deployment
- [ ] 5.5 Document setup and usage