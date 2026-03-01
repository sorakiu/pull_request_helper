FROM python:3.12-slim as builder

WORKDIR /app

# Install Tailscale via official apt repository (avoids curl-pipe-to-shell)
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg && \
    curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg \
        | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null && \
    curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list \
        | tee /etc/apt/sources.list.d/tailscale.list && \
    apt-get update && apt-get install -y --no-install-recommends tailscale && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY backend/ .
COPY frontend/dist/ static/

RUN python manage.py collectstatic --noinput

FROM gcr.io/distroless/python3-debian12

COPY --from=builder /root/.local /home/nonroot/.local
COPY --from=builder /app /app
COPY --from=builder /usr/bin/tailscaled /usr/bin/tailscaled
COPY --from=builder /usr/sbin/tailscale /usr/sbin/tailscale

WORKDIR /app

ENV PATH=/home/nonroot/.local/bin:$PATH

EXPOSE 8080

USER nonroot

COPY docker-entrypoint.py /app/docker-entrypoint.py
ENTRYPOINT ["python", "/app/docker-entrypoint.py"]