FROM python:3.9-alpine

WORKDIR /app
RUN apk add --no-cache curl
COPY requirements.txt .
RUN pip install -r requirements.txt uvloop
COPY main.py .

LABEL maintainer="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.licenses="MIT License"
LABEL org.opencontainers.image.authors="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.url="https://github.com/Galarzaa90/TibiaStatic"
LABEL org.opencontainers.image.source="https://github.com/Galarzaa90/TibiaStatic"
LABEL org.opencontainers.image.vendor="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.title="TibiaStatic"
LABEL org.opencontainers.image.description="An aiohttp server that acts as proxy for resources in static.tibia.com"

EXPOSE 8000
EXPOSE 8001
ENV PYTHONBUFFERED=1
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD sh -c 'if command -v curl >/dev/null 2>&1; then curl -fsS http://localhost:8000/healthcheck >/dev/null; elif command -v wget >/dev/null 2>&1; then wget -q -O - http://localhost:8000/healthcheck >/dev/null; else exit 1; fi'
ENTRYPOINT ["python", "main.py"]
