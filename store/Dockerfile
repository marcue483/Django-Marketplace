FROM python:3.11-slim AS builder

WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install --prefix=/install fastapi uvicorn

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# store/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
