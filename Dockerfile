# Pull base image
FROM python:3.10-slim
# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV RUN_IN_DOCKER 1

RUN apt-get update && apt-get install -y --no-install-recommends netcat

WORKDIR /src/

COPY ./requirements.txt /src/requirements.txt
COPY ./src/db/migrations /src/migrations
COPY ./alembic.ini /src/alembic.ini
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./src /src/src
COPY ./src/db/entrypoint.sh /usr/src/app/entrypoint.sh
EXPOSE 8080
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

