FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install uvloop
EXPOSE 8000
EXPOSE 8001
ENTRYPOINT ["python", "main.py"]