FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/dist/ static/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "pr_helper.wsgi:application", "--bind", "0.0.0.0:8000"]