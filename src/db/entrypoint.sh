#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"


alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload