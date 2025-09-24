# Use official Python image with 3.12 runtime
FROM python:3.12-slim

ARG APP_USER=app
ARG APP_GROUP=app
ARG APP_UID=1000
ARG APP_GID=1000

# Don't buffer stdout/stderr and ensure consistent workspace
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_USER=${APP_USER} \
    APP_GROUP=${APP_GROUP} \
    APP_UID=${APP_UID} \
    APP_GID=${APP_GID}

# Set working directory inside container
WORKDIR /app

# Install system dependencies (if needed for builds)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential bash gosu libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create application user and group with configurable UID/GID defaults
RUN groupadd --gid ${APP_GID} ${APP_GROUP} \
    && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home --home-dir /home/${APP_USER} --shell /bin/bash ${APP_USER}

# Install Python dependencies first to leverage Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remainder of the project
COPY . .

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the development server port
EXPOSE 8000

# Default command runs the Django development server
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
