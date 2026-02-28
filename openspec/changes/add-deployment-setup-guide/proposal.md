# Change: Add comprehensive deployment setup guide

## Why
The repository currently lacks detailed instructions for setting up the infrastructure and secrets needed for CI/CD deployment. This makes it difficult for new contributors or deployments to configure the project properly, leading to failed deployments and wasted time.

## What Changes
- Add comprehensive setup guide to README.md covering GCP project setup, GitHub OAuth configuration, secret management, and all prerequisites for the deploy.yml workflow
- Document all required GitHub repository secrets and their generation methods
- Include step-by-step instructions for GCP service configuration
- Add troubleshooting section for common deployment issues

## Impact
- Affected specs: deployment-setup (new capability)
- Affected code: README.md (documentation updates)