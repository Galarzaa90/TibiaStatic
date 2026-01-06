FROM python:3.9-alpine

WORKDIR /app
RUN apk add --no-cache curl
COPY requirements.txt .
RUN pip install -r requirements.txt uvloop
COPY main.py .
EXPOSE 8000
EXPOSE 8001
ENV PYTHONBUFFERED=1
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD sh -c 'if command -v curl >/dev/null 2>&1; then curl -fsS http://localhost:8000/healthcheck >/dev/null; elif command -v wget >/dev/null 2>&1; then wget -q -O - http://localhost:8000/healthcheck >/dev/null; else exit 1; fi'
ENTRYPOINT ["python", "main.py"]
