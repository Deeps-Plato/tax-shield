# Tax Shield

Private tax deduction cross-reference and form generation tool for a small group of associates (~5-20 users). Cross-references purchases and expenses against tax deduction/credit eligibility, verifies strategies from tax professionals, and generates draft tax forms.

## Requirements

- Python 3.12+
- Docker & Docker Compose (for PostgreSQL)
- Anthropic API key (for AI features)
- Plaid API credentials (optional, for bank integration)

## Quick Start

```bash
# 1. Clone and enter project
cd ~/claude/tax-shield

# 2. Start PostgreSQL
docker compose up -d

# 3. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -e ".[dev]"

# 5. Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and secrets

# 6. Run database migrations
alembic upgrade head

# 7. Start the server
uvicorn tax_shield.main:app --port 8000 --reload
```

Open http://127.0.0.1:8000 — the first admin account is auto-created from `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `.env`.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `JWT_SECRET_KEY` | Yes | Secret for signing JWT tokens |
| `FIELD_ENCRYPTION_KEY` | Yes | 32-byte hex key for AES-256-GCM encryption |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for AI features |
| `ADMIN_EMAIL` | Yes | Auto-created admin account email |
| `ADMIN_PASSWORD` | Yes | Auto-created admin account password |
| `PLAID_CLIENT_ID` | No | Plaid client ID for bank integration |
| `PLAID_SECRET` | No | Plaid secret key |
| `PLAID_ENV` | No | Plaid environment (sandbox/development/production) |

## Architecture

```
src/tax_shield/
  main.py                    # FastAPI app, lifespan, routers
  config.py                  # pydantic-settings
  database.py                # SQLAlchemy async engine
  security.py                # JWT, bcrypt, AES-256-GCM
  dependencies.py            # Auth dependencies

  models/
    db_models.py             # 11 SQLAlchemy ORM models
    api_models.py            # Pydantic request/response schemas

  routes/                    # 12 API route modules
    auth.py                  # Register, login, JWT refresh
    items.py                 # Tax deduction/credit items CRUD
    categories.py            # Category listing
    strategies.py            # Tax strategies CRUD
    search.py                # Full-text search
    user_items.py            # Bookmarked/saved items
    transactions.py          # Bank transactions + CSV upload
    analysis.py              # AI synergy analysis + questionnaire
    tax_records.py           # Tax year records
    tax_forms.py             # PDF form generation
    plaid.py                 # Plaid bank integration
    admin.py                 # Seed data, stats, user management

  services/                  # Business logic
    search_service.py        # PostgreSQL FTS + ILIKE fallback
    analysis_service.py      # Claude AI synergy analysis
    questionnaire_service.py # Smart expense questionnaire
    plaid_service.py         # Plaid Link + transaction sync
    csv_import_service.py    # CSV statement parsing
    transaction_classifier.py # Rules + AI transaction classification
    tax_form_service.py      # Form computation + PDF generation
    seed_service.py          # Seed data loader

  seed_data/                 # Pre-populated reference data
    categories.json          # 18 tax categories
    items.json               # 206 deduction/credit items
    strategies.json          # 30 tax strategies
    questionnaire_templates.json

  forms/templates/           # Tax form field definitions + PDF layout
    f1040.py, schedule_c.py, schedule_a.py, schedule_d.py,
    f1120s.py, f1065.py, w2.py, f1099.py

static/                      # Vanilla JS SPA + Tailwind CSS
  index.html                 # PWA-enabled, mobile-responsive
  manifest.json              # PWA manifest
  sw.js                      # Service worker (offline support)
```

## Features

- **Tax Item Database** — 206 pre-populated deductions/credits with IRS references
- **Smart Questionnaire** — AI-driven Q&A discovers applicable deductions based on user profile
- **Bank Integration** — Plaid SDK for automatic transaction import, CSV upload fallback
- **Transaction Classification** — Rules-based merchant matching + Claude AI for ambiguous items
- **Synergy Analysis** — AI identifies overlapping benefits and optimization opportunities
- **Tax Form Generation** — Draft PDFs for 1040, Schedule A/C/D, 1120-S, 1065, W-2, 1099
- **Full-Text Search** — PostgreSQL FTS across items, strategies, and categories
- **PWA** — Installable on iPhone/Android via "Add to Home Screen"
- **Role-Based Access** — Admin and user roles with JWT authentication

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=tax_shield

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/
```

## Test Flow

1. Register at http://127.0.0.1:8000 and log in
2. Search "laptop" to see matching deductions
3. Save items to My Items with notes and estimated savings
4. Upload a CSV bank statement or link via Plaid
5. Run the smart questionnaire to discover new deductions
6. Run AI synergy analysis on saved items
7. Generate a Schedule C draft and download the PDF

## Security

- Passwords hashed with bcrypt
- JWT access tokens (15 min) + refresh tokens (7 days)
- Plaid tokens encrypted with AES-256-GCM at rest
- CORS locked to configured origins
- HTTPS required in production (reverse proxy)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.x (async) |
| Database | PostgreSQL 16 (Docker) |
| Auth | JWT + bcrypt + AES-256-GCM field encryption |
| Frontend | Vanilla JS (ES modules) + Tailwind CSS CDN |
| Bank Integration | Plaid SDK + CSV upload |
| AI | Anthropic claude-sonnet-4-6 |
| PDF | ReportLab |
