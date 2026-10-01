# ScoreRaven

Computer-based testing (CBT) platform for authoring, dispatching, taking, grading, and releasing exam results.

## Features

- Role-based access: admin, grader, candidate
- Question types: single-answer, multi-answer, true/false, written
- Timed attempts — server-authoritative clock, resume on disconnect, answers autosave
- Per-candidate randomized question order
- Bulk dispatch via CSV or plain email list, with skipped-email reporting
- Blind grading queue for written answers, with regrade and audit history
- Immediate, manual, and scheduled results release, with email notifications
- Background jobs: auto-expire dispatches, auto-submit overdue attempts, release stale claims, scheduled release

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- **Database:** PostgreSQL
- **Background jobs:** Celery + Redis
- **Email:** Resend
- **Frontend:** Bootstrap 5 (dark theme) + custom CSS
- **Deployment:** Docker / Docker Compose

## Setup

### Requirements

- Python 3.12+
- PostgreSQL
- Redis

### Local install

```bash
git clone https://github.com/inistack/ScoreRaven.git
cd ScoreRaven
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in values, see below
flask db upgrade
flask create-user --email admin@example.com --name "Admin" --role admin
```

### Environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session/signing key |
| `DATABASE_URL` | PostgreSQL connection string |
| `RESEND_API_KEY` | Resend API key |
| `EMAIL_FROM` | Sender address for outgoing email |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | Redis connection URL |
| `APP_BASE_URL` | Base URL used to build links in emails |

### Running locally

```bash
flask run
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info
```

### Docker

```bash
docker compose up --build
```

## Usage

1. **Admin** authors a test — questions, difficulty, time limit, validity window, release mode.
2. **Admin** dispatches it via CSV or a plain email list.
3. **Candidate** takes the test within the validity window; timing is server-enforced.
4. Objective questions auto-score; written answers route to the grading queue.
5. Results release immediately, manually, or on a schedule — candidates are notified by email.

## Project Structure

```
app/
  admin/ auth/ candidate/ grading/ dashboard/ main/   # blueprints
  models/        # SQLAlchemy models
  services/      # business logic
  emails/        # email senders and templates
  tasks.py       # Celery tasks
  celery_app.py  # Celery configuration
migrations/      # Alembic migrations
```

## CLI

```bash
flask create-user --email <email> --name <name> --role <admin|grader>
```

## License

Proprietary — all rights reserved.
