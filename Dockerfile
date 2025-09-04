FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R django:django /app

# Copy project files
COPY --chown=django:django . .

# Collect static files (if in production)
ARG DJANGO_ENV=development
RUN if [ "$DJANGO_ENV" = "production" ]; then \
        python manage.py collectstatic --noinput; \
    fi

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "Waiting for postgres..."\n\
while ! nc -z $DB_HOST $DB_PORT; do\n\
  sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
\n\
# Run migrations\n\
python manage.py migrate\n\
\n\
# Create superuser if it doesnt exist\n\
python manage.py shell -c "\n\
from django.contrib.auth import get_user_model\n\
User = get_user_model()\n\
if not User.objects.filter(is_superuser=True).exists():\n\
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')\n\
    print('Superuser created')\n\
else:\n\
    print('Superuser already exists')\n\
"\n\
\n\
# Start the application\n\
exec "$@"' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && chown django:django /app/entrypoint.sh

# Switch to non-root user
USER django

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "itms.wsgi:application"]