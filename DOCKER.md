# Docker Setup Guide

## Quick Start

### Build & Run with Docker Compose

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### API Access

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API: http://localhost:8000

### Initialize Database

```bash
docker-compose exec api python init_db.py
```

### Run Tests

```bash
docker-compose exec api python smoke_test.py --url http://localhost:8000
```

### Access Container Shell

```bash
docker-compose exec api /bin/bash
```

## Manual Docker Commands

### Build Image

```bash
docker build -t hayvan-api:latest .
```

### Run Container

```bash
docker run -d \
  --name hayvan-api \
  -p 8000:8000 \
  -v $(pwd)/animal_tracking.db:/app/animal_tracking.db \
  -e FORM_GEN_INTERVAL_HOURS=12 \
  hayvan-api:latest
```

### View Logs

```bash
docker logs -f hayvan-api
```

### Stop Container

```bash
docker stop hayvan-api
docker rm hayvan-api
```

## Docker Compose with Environment File

Create `.env.docker`:

```
FORM_GEN_INTERVAL_HOURS=12
PYTHONUNBUFFERED=1
```

Update `docker-compose.yml`:

```yaml
services:
  api:
    env_file:
      - .env.docker
```

Then:

```bash
docker-compose up -d
```

## Multi-stage Build (Advanced)

For production, use multi-stage build to reduce image size:

```dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Debugging

### Check image

```bash
docker images | grep hayvan
```

### Inspect container

```bash
docker inspect hayvan-api
```

### Check port binding

```bash
docker port hayvan-api
```

### View running containers

```bash
docker ps
```

## Troubleshooting

### Port already in use

```bash
docker ps  # Find conflicting container
docker stop <container_id>
```

### Database locked

```bash
docker-compose down -v
docker-compose up -d
docker-compose exec api python init_db.py
```

### Permission denied

```bash
docker-compose exec --user root api bash
```

### Check image size

```bash
docker images --format "table {{.Repository}}\t{{.Size}}"
```
