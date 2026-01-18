<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md - Pull Request Helper

This document provides comprehensive guidelines for agentic coding assistants working on the Pull Request Helper project. Follow these conventions to maintain code quality and consistency.

## Project Overview

**Pull Request Helper** is a portfolio project for bulk pull request creation and management.

- **Frontend**: React + Vite with TypeScript
- **Backend**: Django (planned)
- **Purpose**: Portfolio project demonstrating modern web development practices

## Development Environment Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ and pip (for backend)
- Git

### Frontend Setup
```bash
cd frontend
npm install
```

### Backend Setup (Future)
**IMPORTANT**: All Python development must be done inside a virtual environment to avoid polluting the system Python installation. Always create and activate a venv before installing packages.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django
```

#### Code Formatting / Linting
Use Black for Python code formatting and linting:
```bash
# Install Black
pip install black

# Format code
black .

# Check formatting
black --check .
```

## Build, Lint & Test Commands

All commands should be run from the `frontend/` directory.

### Development
```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Quality
```bash
# Run ESLint
npm run lint

# Auto-fix ESLint issues
npm run lint:fix
```

### Testing with Vitest

First, install Vitest and testing dependencies:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom jsdom
```

Add to `package.json` scripts:
```json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest --coverage",
    "test:ui": "vitest --ui"
  }
}
```

#### Running Tests
```bash
# Run all tests once
npm run test

# Run tests in watch mode
npm run test:watch

# Run single test file
npm run test src/components/Button.test.tsx

# Run tests with coverage
npm run test:coverage

# Open test UI
npm run test:ui
```

#### Test File Structure
```typescript
// src/components/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Button from './Button'

test('renders button with text', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
})
```

## TypeScript Migration Guide

### Step 1: Install TypeScript Dependencies
```bash
npm install --save-dev typescript @types/react @types/react-dom @types/node
```

### Step 2: Create tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Step 3: Convert Files
- Rename `.jsx` files to `.tsx`
- Add type annotations to function parameters and return types
- Use TypeScript interfaces for component props

### Step 4: Update ESLint
```bash
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

Update `eslint.config.js`:
```javascript
import tseslint from '@typescript-eslint/eslint-plugin'
import tsparser from '@typescript-eslint/parser'

// Add to rules
{
  files: ['**/*.{ts,tsx}'],
  languageOptions: {
    parser: tsparser,
  },
  plugins: {
    '@typescript-eslint': tseslint,
  },
  rules: {
    ...tseslint.configs.recommended.rules,
  },
}
```

## Code Style Guidelines

### Imports
```typescript
// Group imports: React, third-party libraries, local imports
import React, { useState, useEffect } from 'react'
import { Button } from '@mui/material'
import axios from 'axios'

import { apiService } from '../services/api'
import { User } from '../types/user'
import Button from './Button'
```

### Naming Conventions
- **Components**: PascalCase (`UserProfile`, `PullRequestList`)
- **Functions/Variables**: camelCase (`fetchUserData`, `isLoading`)
- **Constants**: UPPER_CASE (`API_BASE_URL`, `MAX_RETRY_COUNT`)
- **Files**: kebab-case for components (`user-profile.tsx`), camelCase for utilities (`apiService.ts`)
- **Types/Interfaces**: PascalCase (`UserData`, `ApiResponse`)

### React Components
```typescript
// Use functional components with hooks
interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
  onClick: () => void
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  onClick
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

### Error Handling
```typescript
// Helper to safely extract error message
const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) return error.message
  return String(error)
}

// Use try-catch for async operations
const fetchUser = async (userId: string): Promise<User | null> => {
  try {
    const response = await apiService.get(`/users/${userId}`)
    return response.data
  } catch (error) {
    const errorMessage = getErrorMessage(error)
    console.error('Failed to fetch user:', error)
    throw new Error(`User fetch failed: ${errorMessage}`)
  }
}

// Use error boundaries for React components
class ErrorBoundary extends React.Component {
  // Implementation...
}
```

### TypeScript Types
```typescript
// Define interfaces for data structures
interface PullRequest {
  id: number
  title: string
  description: string
  status: 'open' | 'closed' | 'merged'
  createdAt: Date
  author: User
}

// Use union types for component variants
type ButtonSize = 'small' | 'medium' | 'large'
type ButtonColor = 'primary' | 'secondary' | 'danger'
```

## Project Structure

```
frontend/
├── public/                    # Static assets
│   ├── vite.svg
│   └── favicon.ico
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Shared components (Button, Modal, etc.)
│   │   └── features/        # Feature-specific components
│   ├── pages/               # Page components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API services
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── styles/              # Global styles and CSS variables
│   ├── constants/           # Application constants
│   └── lib/                 # Third-party library configurations
├── tests/                   # Test utilities and setup
├── index.html
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
└── package.json
```

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/add-pull-request-form

# Make changes, then commit
git add .
git commit -m "feat: add pull request creation form

- Add form validation
- Implement API integration
- Add loading states"

# Push and create PR
git push origin feature/add-pull-request-form
```

### Commit Message Convention
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure CI passes
4. Request review
5. Address feedback
6. Squash merge to `main`

## CI/CD with GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      run: |
        cd frontend
        npm ci

    - name: Run linter
      run: |
        cd frontend
        npm run lint

    - name: Run tests
      run: |
        cd frontend
        npm run test:coverage

    - name: Build
      run: |
        cd frontend
        npm run build
```

## Quality Assurance

### Pre-commit Hooks
Install Husky for pre-commit hooks:
```bash
npm install --save-dev husky lint-staged
npx husky init
```

Configure `lint-staged` in `package.json`:
```json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "vitest run"],
    "*.{css,scss}": ["stylelint --fix"]
  }
}
```

### Performance Guidelines
- Use React.memo for expensive components
- Implement lazy loading for routes
- Optimize bundle size with code splitting
- Use React DevTools Profiler for performance monitoring

### Accessibility
- Use semantic HTML elements
- Add ARIA labels where needed
- Ensure keyboard navigation works
- Test with screen readers

## Deployment

### Build Optimization
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@mui/material']
        }
      }
    }
  }
})
```

### Environment Configuration
Create `.env` files:
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Pull Request Helper

# .env.production
VITE_API_BASE_URL=https://api.pullrequesthelper.com
VITE_APP_NAME=Pull Request Helper
```

### Docker Setup (Optional)
```dockerfile
# Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

## Backend Integration (Future)

When implementing the Django backend:

1. **API Design**: RESTful endpoints with OpenAPI documentation
2. **Authentication**: JWT tokens with refresh mechanism
3. **Database**: PostgreSQL with Django ORM
4. **Testing**: Django test framework with pytest
5. **Deployment**: Docker containers with Gunicorn

## Additional Resources

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vitest Documentation](https://vitest.dev/)
- [Django Documentation](https://docs.djangoproject.com/)

Remember: Always run tests and linting before committing. Follow the established patterns and conventions to maintain code quality across the project.