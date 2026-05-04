# Hunmin REST API + CLI image
FROM python:3.11-slim AS base

WORKDIR /app

# 의존성 우선 설치 (build cache)
COPY pyproject.toml README.md ./
COPY hunmin/ ./hunmin/

RUN pip install --no-cache-dir -e ".[cjk]" \
    && pip install --no-cache-dir fastapi uvicorn[standard]

# REST API 서버
EXPOSE 8000

# 기본 entrypoint: REST API. CLI 사용은 `docker run --entrypoint hunmin ...`
CMD ["uvicorn", "hunmin.server:app", "--host", "0.0.0.0", "--port", "8000"]
