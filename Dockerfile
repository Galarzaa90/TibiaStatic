FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt uvloop
COPY main.py .
COPY healthcheck.py .
EXPOSE 8000
EXPOSE 8001
ENV PYTHONBUFFERED=1
HEALTHCHECK CMD python healthcheck.py
ENTRYPOINT ["python", "main.py"]