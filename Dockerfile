FROM python:3.12-slim as builder

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY backend/ .
COPY frontend/dist/ static/

RUN python manage.py collectstatic --noinput

FROM gcr.io/distroless/python3-debian12

COPY --from=builder /root/.local /home/nonroot/.local
COPY --from=builder /app /app

WORKDIR /app

ENV PATH=/home/nonroot/.local/bin:$PATH

EXPOSE 8000

USER nonroot

CMD ["/home/nonroot/.local/bin/gunicorn", "pr_helper.wsgi:application", "--bind", "0.0.0.0:8000"]