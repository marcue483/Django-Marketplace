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
