FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY *.py ./
COPY database/ ./database/

RUN mkdir -p /app/sessions && chmod 777 /app/sessions
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

VOLUME ["/app/sessions"]

ENV API_ID=""
ENV API_HASH=""
ENV BOT_TOKEN=""
ENV OWNER_ID=""
ENV ADMIN_IDS=""
ENV DB_URI=""
ENV DB_NAME="tmdb_poster_bot"
ENV TMDB_API_KEY=""
ENV SESSION_NAME="/app/sessions/tmdb_poster_bot"
ENV PLOT_MAX_CHARS="300"
ENV API_TIMEOUT="15"
ENV KEEP_ALIVE="true"
ENV PORT="8000"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "bot.py"]
