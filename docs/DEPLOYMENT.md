# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- uv (recommended) or pip
- Git

### Setup
```bash
# Clone
git clone <repo-url>
cd kisan-dost

# Install with uv (fast)
uv sync

# Or with pip
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run CLI
```bash
# Interactive mode
python -m kisan_dost.cli.main

# With options
python -m kisan_dost.cli.main --help
```

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=kisan_dost --cov-report=html

# Specific module
pytest tests/unit/test_tools/ -v
```

### Code Quality
```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy kisan_dost
```

## Production Deployment

### Environment Variables
Required:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

Optional:
```env
# Real APIs
USE_REAL_APIS=true

# Session backend
SESSION_BACKEND=redis
REDIS_URL=redis://localhost:6379/0

# Tracing
AGENTS_SDK_TRACING_ENABLED=true
AGENTS_SDK_TRACE_EXPORT=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/kisan_dost.log
LOG_FORMAT=json
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Create non-root user
RUN useradd -m -u 1000 kisan && chown -R kisan:kisan /app
USER kisan

# Run
CMD ["python", "-m", "kisan_dost.cli.main"]
```

```bash
# Build
docker build -t kisan-dost .

# Run
docker run -it --env-file .env kisan-dost
```

### Docker Compose (with Redis)

```yaml
# docker-compose.yml
version: '3.8'

services:
  kisan-dost:
    build: .
    env_file: .env
    depends_on:
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./traces:/app/traces

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/kisan-dost.service
[Unit]
Description=Kisan Dost Agronomy Agent
After=network.target redis.service

[Service]
Type=simple
User=kisan
WorkingDirectory=/opt/kisan-dost
EnvironmentFile=/opt/kisan-dost/.env
ExecStart=/opt/kisan-dost/.venv/bin/python -m kisan_dost.cli.main
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable kisan-dost
sudo systemctl start kisan-dost
sudo journalctl -u kisan-dost -f
```

## Cloud Deployment

### AWS (ECS Fargate)
1. Push Docker image to ECR
2. Create ECS task definition with:
   - CPU: 512, Memory: 1024
   - Environment variables from Secrets Manager
   - CloudWatch log group
3. Create service with ALB for health checks

### Google Cloud Run
```bash
# Build and deploy
gcloud run deploy kisan-dost \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="LLM_PROVIDER=openai,OPENAI_API_KEY=..."
```

### Azure Container Instances
```bash
az container create \
  --resource-group myRG \
  --name kisan-dost \
  --image myregistry.azurecr.io/kisan-dost:latest \
  --environment-variables LLM_PROVIDER=openai OPENAI_API_KEY=... \
  --cpu 1 --memory 2
```

## Session Backend Options

### SQLite (Default, Local)
- File-based, no extra infrastructure
- Good for single-instance deployments
- Path: `data/sessions.db`

### Redis (Production, Multi-instance)
```env
SESSION_BACKEND=redis
REDIS_URL=redis://localhost:6379/0
```
- Shared sessions across replicas
- Automatic TTL cleanup
- Pub/sub for real-time features

### In-Memory (Testing Only)
```env
SESSION_BACKEND=memory
```
- Lost on restart
- Fastest for tests

## Monitoring & Observability

### Logging
Structured JSON logs to file:
```env
LOG_FORMAT=json
LOG_FILE=logs/kisan_dost.log
```

### Tracing
OpenAI Agents SDK tracing:
```env
AGENTS_SDK_TRACING_ENABLED=true
AGENTS_SDK_TRACE_EXPORT=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
```

### Metrics (Prometheus)
Add to `config/settings.py`:
```python
# Prometheus metrics
PROMETHEUS_ENABLED: bool = False
PROMETHEUS_PORT: int = 9090
```

### Health Check Endpoint
For container orchestration:
```python
# Add to cli/main.py
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}
```

## Backup & Recovery

### Session Data
```bash
# Backup SQLite
cp data/sessions.db backups/sessions_$(date +%Y%m%d).db

# Backup Redis
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb backups/redis_$(date +%Y%m%d).rdb
```

### Data Files
```bash
# Version control data/
git add data/
git commit -m "Update crop/pest/mandi data"
```

## Security Checklist

- [ ] API keys in `.env` (never committed)
- [ ] `.env` in `.gitignore`
- [ ] Non-root user in Docker
- [ ] Read-only filesystem where possible
- [ ] Network policies (restrict egress)
- [ ] Secrets in vault (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
- [ ] Regular dependency updates (`uv pip install --upgrade`)
- [ ] Security scanning (`pip-audit`, `trivy`)

## Scaling Considerations

### Horizontal Scaling
- Stateless agents → run multiple replicas
- Shared Redis session store
- Load balancer for CLI (if web frontend added)

### Caching
- Cache weather API responses (5 min TTL)
- Cache mandi prices (1 hour TTL)
- Memoize tool results for identical inputs

### Database
- Migrate CSV → PostgreSQL for large datasets
- Add indexes on district, commodity, date
- Read replicas for query scaling

## Rollback Procedure

```bash
# Docker
docker tag kisan-dost:latest kisan-dost:rollback-$(date +%Y%m%d)
docker run -it --env-file .env kisan-dost:rollback-20240115

# Git
git revert HEAD
uv sync
python -m kisan_dost.cli.main
```

## Troubleshooting

### Common Issues

**Agent not responding**
- Check OpenAI API key validity
- Verify model name exists
- Check rate limits

**Session not persisting**
- Verify SQLite file permissions
- Check Redis connection
- Verify SESSION_TTL_HOURS

**Tools returning mock data**
- Ensure `USE_REAL_APIS=true`
- Check API connectivity
- Review service logs

**Guardrails blocking valid queries**
- Check input guardrail patterns
- Review off-topic word list
- Adjust pesticide safety limits

### Debug Mode
```bash
python -m kisan_dost.cli.main --debug
```

Or set:
```env
LOG_LEVEL=DEBUG
```