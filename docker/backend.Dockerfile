FROM python:3.12-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
RUN groupadd --gid 10001 fileshield && useradd --uid 10001 --gid fileshield --no-create-home fileshield
WORKDIR /app
COPY --from=build /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels \
    && mkdir -p /data/jobs && chown -R 10001:10001 /data
COPY fileshield ./fileshield
COPY backend ./backend
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-proxy-headers"]