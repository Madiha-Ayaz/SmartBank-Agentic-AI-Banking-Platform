# SmartBank Developer Guide

## Project Structure
```
SmartBank/
├── agents/
│   ├── classification_agent/   # Intent classification (Phase 02)
│   └── customer_assistant/     # Zara AI assistant (Phase 06)
├── api/                        # OpenAPI 3.1 spec + Postman (Phase 07)
├── architecture/               # Architecture doc (Phase 01)
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── auth.py                 # JWT authentication
│   └── database.py             # SQLAlchemy setup
├── cicd/                       # GitHub Actions + meta-prompts (Phase 08)
├── demo/                       # Demo script (Phase 09)
├── docs/                       # Documentation
├── document_ai/                # Document AI pipeline (Phase 05)
├── robots/                     # RPA robots (Phase 04)
│   ├── audit_logger/
│   ├── cbs_connector/
│   ├── document_generation/
│   └── notification_dispatcher/
├── workflows/                  # BPMN 2.0 workflow files (Phase 03)
└── ui/                         # React frontend
    └── src/
        ├── components/
        ├── pages/
        └── App.css
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (React)
```bash
cd ui
npm install
npm run dev     # Development on :5173
npm run build   # Production build
```

### Running Tests
```bash
python -m pytest              # All tests
python -m pytest agents/      # AI agent tests
python -m pytest robots/      # RPA robot tests
python -m pytest document_ai/ # Document AI tests
```

## Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

## Adding a New Request Type
1. Add intent code to `agents/classification_agent/classifier.py`
2. Create BPMN sub-process in `workflows/`
3. Add route in `backend/main.py`
4. Add robot template in `robots/notification_dispatcher/robot.py`

## Database
SQLite is used for development. For production, set `DATABASE_URL` to PostgreSQL.
```bash
# Schema auto-created on first startup
```

## API Versioning
All new endpoints should use `/v1/` prefix. Deprecated endpoints carry `X-Sunset` header.
