# Wambaza Backend

FastAPI backend for [Wambaza](https://github.com/dianepretty/wambaza) — a multilingual adolescent sexual and reproductive health (ASRH) platform serving English, Kinyarwanda, and Luganda speakers in Rwanda and Uganda.

## Prerequisites

- Python 3.10+
- PostgreSQL database
- An SMTP account (Gmail with an [App Password](https://myaccount.google.com/apppasswords) works) for sending publisher welcome emails and OTP codes

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET=some-long-random-secret
JWT_EXPIRE_MINUTES=480
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

Run database migrations:

```bash
alembic upgrade head
```

Start the dev server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

---

## API overview

| Router | Prefix | Purpose |
|---|---|---|
| `auth` | `/auth` | Login, logout, OTP-based forgot/reset password, change password, self-service profile (`/auth/me`) |
| `users` | `/users` | Admin-only publisher account management (create, list, edit, activate/deactivate) |
| `articles` | `/articles` | Article CRUD, status workflow (draft/published/archived), header image upload, admin moderation view |
| `model` | `/model` | AI question-answering endpoint (`/model/ask`) — no auth required |

### Auth & roles

- Sessions use an `httponly` JWT cookie set on login (`access_token`)
- Two roles: `admin` and `publisher`
- New publishers are created by an admin via `/users`, get a temporary password emailed to them, and are forced to set a new password (`must_change_password`) on first login
- Forgot password uses a 6-digit OTP emailed to the user, valid for 10 minutes, hashed at rest

### Articles

- Status flow: `draft → published → archived`, with `unpublish` (used by both owners and admins) returning an article to draft
- Header images are uploaded via `POST /articles/upload-image` and served statically from `/static/uploads`
- Each article supports independent title/content fields per language (`_en`, `_kin`, `_lug`); only English is required

## Project structure

```
app/
├── main.py                   # FastAPI app, CORS, static file mount
├── models.py                 # SQLAlchemy models (User, Article)
├── schemas.py                 # Pydantic request/response schemas
├── db/session.py             # DB engine/session
├── api/
│   ├── deps.py                # Auth dependencies (get_current_user, require_admin, require_publisher)
│   └── routers/                # auth, users, articles, model
└── utils/
    ├── security.py            # Password hashing, JWT
    └── emailer.py              # Branded HTML emails (welcome + OTP)
alembic/                       # DB migrations
```

## Migrations

This project uses Alembic. After changing a model in `app/models.py`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```
