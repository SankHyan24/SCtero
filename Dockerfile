FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required (e.g. for SQLite)
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Run with Gunicorn on default container port 5000
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-5000} app:app"]
