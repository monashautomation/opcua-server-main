# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Fail closed: a plain `docker run` cannot start the insecure legacy profile.
    GLADOS_PROFILE=production

RUN groupadd --gid 10001 glados \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin glados

WORKDIR /app

COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY scripts ./scripts
COPY config ./config
RUN pip install --no-cache-dir --no-deps .

USER 10001:10001
EXPOSE 4841
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "/app/scripts/healthcheck.py"]

ENTRYPOINT ["python", "-m", "glados_opcua"]
