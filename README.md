# Wambaza Backend

FastAPI backend for the Wambaza project.

Prerequisites
- Python 3.10+
- PostgreSQL database

Environment
Create a `.env` file based on `.env.example` and set values.

Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs`.
