FROM docker.io/python:3.13.1-slim-bookworm as python

# Stage 1: Build our dependency wheels
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=local

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev

COPY ./requirements .

RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r ${BUILD_ENVIRONMENT}.txt

#Stage 2: Python run stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo git bash-completion nano ssh

RUN addgroup --system fastapi && \
    adduser --system --ingroup fastapi fastapi

RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev \
    gettext \
    && apt-get install -y telnet netcat-traditional \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY --chown=fastapi:fastapi ./compose/local/fastapi/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=fastapi:fastapi ./compose/local/fastapi/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=fastapi:fastapi ./compose/local/fastapi/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=fastapi:fastapi ./compose/local/fastapi/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY --chown=fastapi:fastapi ./compose/local/fastapi/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

COPY --chown=fastapi:fastapi . ${APP_HOME}

RUN chown fastapi:fastapi ${APP_HOME}

USER fastapi

ENTRYPOINT [ "/entrypoint" ]