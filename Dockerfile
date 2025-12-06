FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && apk add --no-cache bash

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project
COPY . .

# Create static directory
RUN mkdir -p staticfiles

# Create and switch to non-root user
RUN adduser -D django \
    && chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "crm_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
