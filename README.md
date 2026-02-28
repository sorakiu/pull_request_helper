# Pull Request Helper

A modern web application for bulk pull request creation across multiple GitHub repositories. This portfolio project demonstrates best practices in full-stack development with React, Django, and GitHub OAuth integration.

## Features

- **GitHub OAuth Authentication**: Secure login with GitHub OAuth 2.0
- **Bulk PR Creation**: Create pull requests across multiple repositories simultaneously
- **Repository Management**: View and select from your accessible GitHub repositories
- **Branch Validation**: Client and server-side validation for branch names and existence
- **Real-time Status**: Asynchronous job processing with progress tracking
- **Responsive Design**: Mobile-friendly interface with modern CSS
- **Comprehensive Testing**: Unit and integration tests for both frontend and backend

## Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling
- **React Router** for client-side routing
- **Axios** for API communication
- **React Toastify** for notifications
- **Vitest** for unit testing
- **Testing Library** for component testing

### Backend
- **Django 5.2** with Django REST Framework
- **PostgreSQL** database
- **Django Allauth** for OAuth authentication
- **Celery** for asynchronous task processing
- **Redis** as message broker
- **Whitenoise** for static file serving

### Infrastructure
- **Docker Compose** for local development
- **GitHub OAuth App** for authentication
- **Django Channels** (planned for real-time updates)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and pip
- PostgreSQL (or Docker)
- Redis (or Docker)
- GitHub OAuth App credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sorakiu/pull_request_helper
   cd pull_request_helper
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose up -d db redis

   # Or set up PostgreSQL manually
   createdb pr_helper
   ```

4. **Environment Variables**

   Create `.env` file in the backend directory:
   ```bash
   # Database
   DB_NAME=pr_helper
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432

   # GitHub OAuth
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret

   # Django
   SECRET_KEY=your_django_secret_key
   DEBUG=True

   # Celery
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start Backend Services**
   ```bash
   # Terminal 1: Start Django server
   cd backend
   python manage.py runserver

   # Terminal 2: Start Celery worker
   celery -A pr_helper worker --loglevel=info
   ```

2. **Start Frontend**
   ```bash
   # Terminal 3: Start Vite dev server
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api/

## GitHub OAuth Setup

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create a new OAuth App with:
   - **Homepage URL**: `http://localhost:8000` (production: your domain)
   - **Authorization callback URL**: `http://localhost:8000/accounts/github/login/callback/`
3. Copy Client ID and Client Secret to your environment variables

## Deployment to Google Cloud

This section provides comprehensive setup instructions for deploying the Pull Request Helper to Google Cloud Platform using GitHub Actions CI/CD.

### Prerequisites

- Google Cloud Platform account with billing enabled
- GitHub account with repository admin permissions
- Terraform CLI (1.6.0+)
- Docker
- Git

### Step 1: Google Cloud Project Setup

1. **Create or select a GCP project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - **Important**: Enable billing for the project (required for most services)

2. **Set up gcloud CLI**
   ```bash
   # Authenticate and set project
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs**
   **Prerequisites**: You must have Project Editor or Owner role in the GCP project.

   Run the following commands (or enable via GCP Console → APIs & Services → Library):
   ```bash
   gcloud services enable run.googleapis.com
   gcloud config set run/region us-central1
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable redis.googleapis.com
   gcloud services enable vpcaccess.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable compute.googleapis.com
   gcloud services enable servicenetworking.googleapis.com
   ```

   **Troubleshooting**: If you get permission denied errors:
   - Verify you're using the correct project ID
   - Confirm billing is enabled
   - Check that you have sufficient IAM permissions
   - Try enabling APIs through the GCP Console instead

3. **Create service account for deployments**
   **Prerequisites**: You must have IAM admin permissions in the GCP project.

   ```bash
   # Set your project ID as an environment variable
   export GOOGLE_PROJECT_ID=your-project-id

   # Create service account
   gcloud iam service-accounts create pr-helper-deploy \
     --description="Service account for PR Helper deployments" \
     --display-name="PR Helper Deploy"

   # Grant required roles
   gcloud projects add-iam-policy-binding $GOOGLE_PROJECT_ID \
     --member="serviceAccount:pr-helper-deploy@${GOOGLE_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/cloudsql.admin"

   gcloud projects add-iam-policy-binding $GOOGLE_PROJECT_ID \
     --member="serviceAccount:pr-helper-deploy@${GOOGLE_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/secretmanager.admin"

   gcloud projects add-iam-policy-binding $GOOGLE_PROJECT_ID \
     --member="serviceAccount:pr-helper-deploy@${GOOGLE_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   gcloud projects add-iam-policy-binding $GOOGLE_PROJECT_ID \
     --member="serviceAccount:pr-helper-deploy@${GOOGLE_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/storage.admin"

   gcloud projects add-iam-policy-binding $GOOGLE_PROJECT_ID \
     --member="serviceAccount:pr-helper-deploy@${GOOGLE_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/compute.networkAdmin"
   ```

   **Troubleshooting**: If you get permission errors:
   - Ensure you have `roles/resourcemanager.projectIamAdmin` role
   - Verify the project ID is correct
   - Check that you're authenticated with the right account

4. **Generate service account key**
   ```bash
   gcloud iam service-accounts keys create gcp-sa-key.json \
     --iam-account=pr-helper-deploy@${GOOGLE_PROJECT_ID}.iam.gserviceaccount.com
   ```

5. **Create Cloud Storage bucket for Terraform state**
   ```bash
   gsutil mb -p $GOOGLE_PROJECT_ID -l us-central1 gs://pr-helper-tf-state-${GOOGLE_PROJECT_ID}
   ```

### Step 2: GitHub OAuth Application Setup

1. **Create GitHub OAuth App**
   - Go to GitHub Settings → Developer settings → OAuth Apps
   - Click "New OAuth App"
   - Fill in application details:
     - **Application name**: Pull Request Helper (Production)
     - **Homepage URL**: `https://pr-helper-YOUR_PROJECT_ID.run.app` (update after deployment)
     - **Authorization callback URL**: `https://pr-helper-YOUR_PROJECT_ID.run.app/accounts/github/login/callback/`
     - **Description**: Optional

2. **Generate client credentials**
   - After creation, copy the Client ID
   - Generate a new Client Secret

### Step 3: Configure GitHub Repository Secrets

Go to your GitHub repository Settings → Secrets and variables → Actions

Add the following repository secrets:

| Secret Name | Description | Source |
|-------------|-------------|--------|
| `GCP_PROJECT_ID` | Your GCP project ID | GCP Console |
| `GCP_SA_KEY` | Service account JSON key | Generated key file content |
| `TF_STATE_BUCKET` | Terraform state bucket name | `pr-helper-tf-state-YOUR_PROJECT_ID` |
| `DB_PASSWORD` | Database password | Generate a strong password |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `pr-helper-YOUR_PROJECT_ID.run.app` |
| `TAILSCALE_ENABLED` | Enable Tailscale (optional) | `false` or `true` |
| `TAILSCALE_AUTH_KEY` | Tailscale auth key (if enabled) | From Tailscale admin console |

### Step 4: Terraform Setup

1. **Install Terraform**
   ```bash
   # Download from https://www.terraform.io/downloads
   terraform version  # Should be 1.6.0+
   ```

2. **Initialize Terraform backend**
   ```bash
   cd terraform
   terraform init -backend-config="bucket=pr-helper-tf-state-YOUR_PROJECT_ID"
   ```

3. **Configure Terraform variables**
   Create a `terraform.tfvars` file or pass variables via command line:
   ```bash
   # terraform.tfvars
   project_id = "YOUR_PROJECT_ID"
   region = "us-central1"
   environment = "production"
   db_password = "YOUR_DB_PASSWORD"  # From secrets
   allowed_hosts = "pr-helper-YOUR_PROJECT_ID.run.app"
   tailscale_enabled = false  # or true
   ```

### Step 5: Deploy

1. **Push changes to trigger deployment**
   ```bash
   git add .
   git commit -m "feat: add deployment configuration"
   git push origin main
   ```

2. **Monitor deployment**
   - Go to GitHub Actions tab
   - Watch the deploy workflow
   - Check Cloud Run console for service status

### Step 6: Post-Deployment Configuration

1. **Update OAuth App URLs**
   - Get the Cloud Run service URL from deployment output
   - Update GitHub OAuth App homepage and callback URLs

2. **Configure Secret Manager**
   - Add secrets to GCP Secret Manager:
   ```bash
   echo -n "your-django-secret-key" | gcloud secrets create django-secret-key --data-file=-
   echo -n "your-github-client-id" | gcloud secrets create github-client-id --data-file=-
   echo -n "your-github-client-secret" | gcloud secrets create github-client-secret --data-file=-
   echo -n "your-tailscale-auth-key" | gcloud secrets create tailscale-auth-key --data-file=-
   echo -n "your-db-password" | gcloud secrets create db-password --data-file=-
   ```

3. **Run database migrations**
   - Migrations are run automatically during deployment
   - Monitor the migration job in Cloud Run jobs

### Local Development Setup

For testing deployment configurations locally:

1. **Required tools**
   - Node.js 18+
   - Python 3.11+
   - Docker & Docker Compose
   - Terraform 1.6.0+
   - Google Cloud SDK

2. **Environment setup**
   ```bash
   # Authenticate with GCP
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID

   # Install Terraform
   # Follow Terraform installation guide

   # Clone and setup
   git clone https://github.com/your-org/pull_request_helper
   cd pull_request_helper
   ```

3. **Local secrets**
   - Create local `.env` files for development
   - Use GCP Secret Manager for production secrets

### Troubleshooting

#### Common Deployment Issues

1. **Terraform backend access denied**
   - Ensure TF_STATE_BUCKET secret is correct
   - Verify service account has storage.admin role
   - Check bucket exists and permissions

2. **Cloud Run deployment fails**
   - Check container image exists in Container Registry
   - Verify VPC connector is created
   - Check service account permissions

3. **Database connection issues**
   - Ensure Cloud SQL instance is running
   - Check private IP configuration
   - Verify service account has cloudsql.client role

4. **Secret Manager access denied**
   - Confirm secrets exist in Secret Manager
   - Check service account has secretmanager.secretAccessor role
   - Verify secret versions are set to "latest"

#### Health Check Validation

After deployment, verify the application is working:

1. **Check service URL**
   ```bash
   curl https://pr-helper-YOUR_PROJECT_ID.run.app/health/
   # Should return {"status": "healthy"}
   ```

2. **Test readiness**
   ```bash
   curl https://pr-helper-YOUR_PROJECT_ID.run.app/health/ready/
   # Should return {"status": "ready"}
   ```

3. **Monitor logs**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pr-helper-web" --limit=10
   ```

## API Documentation

### Authentication Endpoints

- `POST /api/logout/` - Logout and delete OAuth token
- `GET /api/csrf/` - Get CSRF token for SPA requests

### Repository Endpoints

- `GET /api/repos/` - List user's GitHub repositories (authenticated)
- `POST /api/jobs/` - Create bulk PR job (authenticated)

### Job Status

Jobs are processed asynchronously. Monitor job status through the Django admin or implement WebSocket connections for real-time updates.

## Development

### Code Quality

- **Linting**: ESLint for frontend, Black for backend
- **Testing**: Vitest for frontend, Django TestCase for backend
- **Type Safety**: TypeScript for frontend, mypy for backend (planned)

### Running Tests

```bash
# Frontend tests
cd frontend
npm run test

# Backend tests
cd backend
python manage.py test
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build:backend

# Collect static files
cd ../backend
python manage.py collectstatic --noinput
```

## Project Structure

```
pull_request_helper/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── App.tsx         # Main application component
│   │   └── main.tsx        # Application entry point
│   ├── package.json
│   └── vite.config.js
├── backend/                  # Django application
│   ├── pr_helper/           # Django project settings
│   ├── bulk_pr/             # Main Django app
│   │   ├── models.py        # Database models
│   │   ├── views.py         # API endpoints
│   │   ├── tasks.py         # Celery tasks
│   │   └── tests.py         # Unit tests
│   ├── requirements.txt
│   └── manage.py
├── docker-compose.yaml       # Development services
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## Security Features

- **OAuth 2.0 Authentication**: Secure token-based authentication
- **CSRF Protection**: Django's built-in CSRF protection
- **Input Validation**: Client and server-side validation
- **Secure Headers**: Django security middleware
- **Token Cleanup**: Automatic token deletion on logout

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for your changes
4. Ensure all tests pass: `npm test && python manage.py test`
5. Follow the existing code style and conventions
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature`
8. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Real-time job status updates with WebSockets
- [ ] PR template support with repository-specific configurations
- [ ] Batch job management and history
- [ ] GitHub App integration for organization-wide access
- [ ] Advanced branch conflict detection
- [ ] Slack/Discord notifications for job completion
- [ ] scheduled jobs / triggered jobs

---

Built with ❤️ as a portfolio project demonstrating modern full-stack development practices.
