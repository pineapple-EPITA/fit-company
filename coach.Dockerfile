FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY src/coach/requirements.txt ./requirements.txt
COPY pyproject.toml uv.lock ./
COPY main_coach.py /app/main_coach.py
COPY src/coach /app/src/coach

RUN pip install --upgrade pip && pip install -r requirements.txt

ENV FLASK_ENV=development
ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "main_coach.py"] 