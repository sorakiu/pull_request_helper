# Tailscale Deployment Guide

This guide explains how to enable optional Tailscale connectivity for private access to the Pull Request Helper application.

## Overview

When enabled, Tailscale provides zero-trust network access to your deployed application without exposing public endpoints. The application will be accessible via its Tailscale IP address instead of (or in addition to) public access.

## Prerequisites

- A Tailscale account and network (tailnet)
- Administrative access to generate auth keys
- GitHub repository secrets configured (see below)

## Setup Steps

### 1. Generate Tailscale Auth Key

1. Log in to the [Tailscale Admin Console](https://login.tailscale.com/admin)
2. Go to **Settings** → **Keys**
3. Click **Generate auth key**
4. Configure the key:
   - **Key expiry**: Choose appropriate expiry (e.g., no expiry for reusable keys)
   - **Key capabilities**: Leave defaults for basic connectivity
   - **Tags**: Leave empty (free plan limitation)
   - **Reusable**: Check this option
   - **Ephemeral**: Uncheck (we want persistent connections)
5. **Important**: Specify which tailnet this key should join by selecting the appropriate network
6. Click **Generate key** and copy the auth key

### 2. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

- `TAILSCALE_ENABLED`: Set to `true` to enable Tailscale
- `TAILSCALE_AUTH_KEY`: Paste the auth key generated above

### 3. Deploy

Push your changes or trigger the deployment workflow. The application will:

1. Install and start Tailscale during container startup
2. Authenticate using the provided auth key
3. Join the specified Tailscale network
4. Become accessible via its Tailscale IP address

### 4. Access the Application

After deployment:

1. Ensure your local machine is connected to the same Tailscale network
2. Find the Tailscale IP of your deployed service:
   ```bash
   # On your local machine connected to Tailscale
   tailscale ip -4  # Shows your Tailscale IP
   ping <deployment-hostname>  # Or check Tailscale admin console
   ```
3. Access the application at `http://<tailscale-ip>:8080`

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `TAILSCALE_ENABLED` | Enable/disable Tailscale connectivity | `false` |
| `TAILSCALE_AUTH_KEY` | Auth key for Tailscale authentication | Required when enabled |

## Security Considerations

- **Auth Keys**: Store keys securely in GitHub secrets, rotate regularly
- **Network Access**: Only machines connected to the same Tailscale network can access the application
- **Zero Trust**: No public endpoints exposed when Tailscale is enabled
- **Key Scope**: Generate keys with minimal required permissions

## Troubleshooting

### Deployment Fails with Tailscale Error

- Verify `TAILSCALE_AUTH_KEY` is set correctly
- Check that the auth key hasn't expired
- Ensure the key is valid for the target network
- Review deployment logs for specific error messages

### Cannot Access Application

- Confirm your local machine is connected to Tailscale
- Verify you're on the same network as the deployment
- Check Tailscale IP assignment in admin console
- Ensure firewall rules allow access

### Application Starts But Tailscale Doesn't Connect

- Check container logs for Tailscale startup messages
- Verify auth key format and permissions
- Confirm network connectivity from the deployment environment

## Disabling Tailscale

To disable Tailscale and return to public access:

1. Set `TAILSCALE_ENABLED=false` in GitHub secrets (or remove the secret)
2. Optionally remove `TAILSCALE_AUTH_KEY` secret
3. Redeploy the application

## Architecture Notes

- Tailscale runs as a sidecar service in the same container
- The application continues to bind to `0.0.0.0:8080`
- Tailscale provides the secure tunnel to this port
- No changes to application code required