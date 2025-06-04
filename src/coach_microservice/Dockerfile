FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app/src

CMD ["python", "app.py"] 