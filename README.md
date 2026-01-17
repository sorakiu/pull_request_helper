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
   git clone https://github.com/yourusername/pull_request_helper.git
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

---

Built with ❤️ as a portfolio project demonstrating modern full-stack development practices.
