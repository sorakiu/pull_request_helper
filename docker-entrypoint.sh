#!/bin/bash
set -e

# Function to start Tailscale
start_tailscale() {
    echo "Starting Tailscale..."

    # Start tailscaled in the background
    /usr/bin/tailscaled --statedir=/tmp/tailscale --socket=/tmp/tailscale.sock &

    # Wait for tailscaled to start
    sleep 2

    # Authenticate with Tailscale using auth key
    if [ -n "$TAILSCALE_AUTH_KEY" ]; then
        echo "Authenticating with Tailscale..."
        /usr/sbin/tailscale --socket=/tmp/tailscale.sock up --authkey="$TAILSCALE_AUTH_KEY" --accept-routes
    else
        echo "ERROR: TAILSCALE_AUTH_KEY not provided"
        exit 1
    fi
}

# Check if Tailscale is enabled
if [ "$TAILSCALE_ENABLED" = "true" ]; then
    start_tailscale
else
    echo "Tailscale disabled, proceeding with normal startup..."
fi

# Start the Django application
echo "Starting Django application..."
exec /home/nonroot/.local/bin/gunicorn pr_helper.wsgi:application --bind 0.0.0.0:8080 --workers 2 --timeout 60