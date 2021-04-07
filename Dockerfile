FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt uvloop
COPY main.py .
EXPOSE 8000
EXPOSE 8001
ENTRYPOINT ["python", "main.py"]