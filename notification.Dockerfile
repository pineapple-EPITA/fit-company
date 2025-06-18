FROM python:3.11-slim

WORKDIR /app

COPY ./src/notification /app

RUN pip install Flask requests pika

CMD ["python", "app.py"]