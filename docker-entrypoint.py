#!/usr/bin/env python3
"""Docker entrypoint script for PR Helper application."""
import os
import subprocess
import sys
import time


_TAILSCALE_SOCKET = "/tmp/tailscale.sock"
_SOCKET_POLL_INTERVAL = 0.5
_SOCKET_POLL_ATTEMPTS = 30


def _wait_for_tailscaled_socket() -> None:
    """Poll for the tailscaled Unix socket until it appears or timeout."""
    for _ in range(_SOCKET_POLL_ATTEMPTS):
        if os.path.exists(_TAILSCALE_SOCKET):
            return
        time.sleep(_SOCKET_POLL_INTERVAL)
    print("ERROR: tailscaled failed to start (socket not found)")
    sys.exit(1)


def start_tailscale():
    """Start Tailscale daemon and authenticate."""
    print("Starting Tailscale...")

    if not os.environ.get("TAILSCALE_AUTH_KEY"):
        print("ERROR: TAILSCALE_AUTH_KEY not provided")
        sys.exit(1)

    # Start tailscaled in userspace-networking mode (no root/CAP_NET_ADMIN needed)
    tailscaled_proc = subprocess.Popen(
        [
            "/usr/bin/tailscaled",
            "--statedir=/tmp/tailscale",
            "--socket=" + _TAILSCALE_SOCKET,
            "--tun=userspace-networking",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    _wait_for_tailscaled_socket()

    # Authenticate via TS_AUTHKEY env var to keep the key out of process listings
    print("Authenticating with Tailscale...")
    env = {**os.environ, "TS_AUTHKEY": os.environ["TAILSCALE_AUTH_KEY"]}
    result = subprocess.run(
        ["/usr/sbin/tailscale", "--socket=" + _TAILSCALE_SOCKET, "up", "--accept-routes"],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print(f"ERROR: Tailscale authentication failed: {result.stderr}")
        sys.exit(1)

    return tailscaled_proc


def main():
    """Main entrypoint."""
    # Check if Tailscale is enabled
    if os.environ.get("TAILSCALE_ENABLED") == "true":
        tailscaled_proc = start_tailscale()
    else:
        print("Tailscale disabled, proceeding with normal startup...")

    # Start the Django application
    print("Starting Django application...")
    os.execvp(
        "/home/nonroot/.local/bin/gunicorn",
        [
            "gunicorn",
            "pr_helper.wsgi:application",
            "--bind", "0.0.0.0:8080",
            "--workers", "2",
            "--timeout", "60"
        ]
    )


if __name__ == "__main__":
    main()
