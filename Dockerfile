# Pull base image
FROM python:3.10-slim
# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV RUN_IN_DOCKER 1

WORKDIR /src/

COPY ./requirements.txt /src/requirements.txt
COPY ./migrations /src/migrations
COPY ./alembic.ini /src/alembic.ini
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./src /src/src
EXPOSE 8080


