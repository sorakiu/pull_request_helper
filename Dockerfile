FROM python:3.12-slim as builder

WORKDIR /app

# Install Tailscale and dependencies
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://tailscale.com/install.sh | sh && \
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

COPY docker-entrypoint.sh /docker-entrypoint.sh
CMD ["/docker-entrypoint.sh"]