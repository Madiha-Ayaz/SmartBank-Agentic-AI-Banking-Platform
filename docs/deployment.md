# SmartBank Deployment Guide

## Local Development
```bash
# Start both backend + frontend
start.bat
```

## Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN cd ui && npm install && npm run build
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Architecture Decisions

### Database
- **Dev**: SQLite (zero config)
- **Prod**: PostgreSQL with SQLAlchemy

### Authentication
- JWT tokens with bcrypt password hashing
- Token expiry: 15 minutes (configurable)

### Frontend
- React + Vite (fast builds)
- Proxy `/api` to backend in dev mode

### Robots
- Python classes wrapping business logic
- UiPath XAML workflows documented in READMEs

## Performance Targets
| Scenario | Target |
|----------|--------|
| API P99 latency | <200ms |
| Document verification | <3s |
| AI classification | <500ms |
| PDF generation | <2s |
| Notification dispatch | <1s |

## Monitoring
- Health endpoint: `GET /api/health`
- Audit trail: `GET /api/audit/logs`
- Robot status: `GET /api/robots/status`
