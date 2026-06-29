# SmartBank API Documentation

## Overview
SmartBank exposes a RESTful API at `/api` for all platform operations.

## Base URL
- Production: `https://api.smartbank.ai/v1`
- Development: `http://localhost:8000/api`

## Authentication
Most endpoints require JWT Bearer token authentication.

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "smartbank123"
}
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 15
}
```

Use the token in subsequent requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Endpoints

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health` | No | Service health + DB status |

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | No | Get JWT token |
| POST | `/api/auth/register` | No | Create user |
| GET | `/api/auth/me` | Yes | Current user info |

### Dashboard
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/dashboard/stats` | No | Aggregated KPIs |
| GET | `/api/dashboard/cases` | No | List/search cases |
| GET | `/api/dashboard/cases/{id}` | No | Single case detail |
| GET | `/api/dashboard/analytics` | No | Status/priority/channel breakdown |

### AI Agents
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/classify` | No | Classify request intent |
| POST | `/api/chat` | No | Chat with Zara AI assistant |
| GET | `/api/assistant/info` | No | Assistant metadata |

### Document AI
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/document/verify` | No | Upload + verify document |

### Audit
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/audit/log` | No | Write audit entry |
| GET | `/api/audit/logs` | No | Get audit trail |

### Customers
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/customers` | No | List customers |
| POST | `/api/customers` | No | Create customer |

### Robots
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/robots/status` | No | Robot health status |
| POST | `/api/robots/notification/send` | No | Send notification via robot |
| POST | `/api/robots/document/generate` | No | Generate document via robot |
| GET | `/api/robots/audit/verify` | No | Verify audit log integrity |

### Workflows
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/workflows` | No | List BPMN workflow files |

## Error Response Format
```json
{
  "detail": "Error description"
}
```

## Rate Limiting
- 100 requests per minute per IP
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Versioning
API versioning via URL prefix (`/v1/`). Current version: 2.0.0.
