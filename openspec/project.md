# Project Context

## Purpose
Pull Request Helper is a portfolio project for bulk pull request creation and management. It demonstrates modern web development practices and provides tools for efficiently managing multiple GitHub pull requests across repositories.

## Tech Stack
- **Frontend**: React + Vite with TypeScript
- **Backend**: Django (planned)
- **Languages**: TypeScript/JavaScript, Python
- **Build Tools**: Vite, npm
- **Testing**: Vitest, @testing-library/react, @testing-library/jest-dom
- **Linting**: ESLint
- **Version Control**: Git
- **Prerequisites**: Node.js 18+, Python 3.11+, npm, pip
- **Virtual Environment**: All Python development must be done inside a virtual environment (e.g., venv) to avoid polluting the system Python installation. Use pyenv or venv for environment management.

## Project Conventions

### Code Style
- **Imports**: Group imports as React/third-party/local, with React imports first
- **Naming**: PascalCase for components, camelCase for functions/variables, UPPER_CASE for constants, kebab-case for files
- **React Components**: Functional components with hooks, TypeScript interfaces for props
- **Error Handling**: Try-catch for async operations, error boundaries for components
- **TypeScript**: Strict mode enabled, proper typing for all components and functions

### Architecture Patterns
- **Frontend Structure**:
  - `components/`: Reusable UI components (common/, features/)
  - `pages/`: Page-level components
  - `hooks/`: Custom React hooks
  - `services/`: API service functions
  - `types/`: TypeScript type definitions
  - `utils/`: Utility functions
  - `styles/`: Global styles and CSS variables
  - `constants/`: Application constants
- **State Management**: React hooks (useState, useEffect) for local state
- **API Integration**: Axios for HTTP requests (planned)

### Testing Strategy
- **Framework**: Vitest with @testing-library/react and jsdom
- **Test Structure**: Component tests in `src/components/*.test.tsx`
- **Coverage**: Run `npm run test:coverage` for coverage reports
- **Requirements**: Tests must pass before commits, focus on user interactions and component behavior

### Git Workflow
- **Branching**: Feature branches from `main` (e.g., `feature/add-pull-request-form`)
- **Commits**: Conventional commits (feat, fix, docs, style, refactor, test, chore)
- **Pull Requests**: Create PRs from feature branches, require review before merge
- **Merge**: Squash merge to `main`

## Domain Context
This project focuses on GitHub pull request management, including:
- Bulk PR creation across multiple repositories
- PR status tracking and management
- Integration with GitHub API for PR operations
- Portfolio demonstration of modern React/TypeScript development

## Important Constraints
- Portfolio project with no production deployment requirements
- Frontend-only implementation currently (backend planned)
- Follows GitHub API rate limits and best practices

## External Dependencies
- **GitHub API**: For pull request operations and repository management
- **Node.js Ecosystem**: npm packages for React, Vite, testing libraries
- **Python Ecosystem**: Django and related packages (planned for backend)
