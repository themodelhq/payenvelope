# PayEnvelope — Backend

A deterministic, rule-based salary-budgeting API. **No machine learning or AI
is used anywhere in this service** — payslip parsing is regular expressions
and arithmetic, and envelope allocation is configurable percentage/fixed/
remainder rules.

## What's implemented vs. what's a stub

This backend is real, runnable, tested code — not scaffolding. What's fully
implemented:

- **Payslip parser** (`app/parser.py`) — regex-based extraction of employee
  name, employer, earnings, statutory deductions, gross/net salary, with
  country-aware label sets for Nigeria (default), Ghana, Kenya, South Africa,
  and a reconciliation check that flags mismatched figures for review.
- **Envelope engine** (`app/envelope_engine.py`) — percentage/fixed/remainder
  allocation rules, plus create/rename/delete/archive/lock/merge/split/
  transfer operations.
- **REST API** (FastAPI) — auth (register/login/me via JWT), payslip parsing
  + persistence, envelope CRUD + lifecycle actions, transactions with
  filtering, and report endpoints (cash flow, expense categories, envelope
  allocation, budget performance). Auto-generated Swagger docs at `/docs`.
- **Database models** (SQLAlchemy) — users, payslips, envelopes, envelope
  rules, transactions, savings goals, bills, notifications, subscriptions,
  audit logs.
- **Tests** — 17 passing pytest cases covering the parser and envelope engine
  (`tests/test_parser.py`, `tests/test_envelope_engine.py`).

What's a documented integration point, not implemented (these require live
third-party credentials/infrastructure this environment can't provision):

- OAuth (Google/Microsoft/Apple) and magic-link login — `auth.create_access_token`
  is ready to be called from an OAuth callback route once you register a
  provider app.
- Paystack/Flutterwave/Stripe billing — `models.Subscription` has a `provider`
  field ready to store this; wire up your webhook handler to update it.
- Push notifications (FCM/OneSignal) — `models.Notification` stores in-app
  notifications now; hook a provider SDK into the same creation path to also
  push externally.
- Redis caching — the app runs fine without it (SQLite/Postgres only); add a
  cache layer in front of the report endpoints if you need it at scale.

## Running locally

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive Swagger docs.

By default this uses a local SQLite file (`payenvelope.db`) so it runs with
zero setup. For Postgres, set `DATABASE_URL`:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/payenvelope"
```

## Running tests

```bash
pytest tests/ -v
```

## Project layout

```
backend/
  app/
    main.py              FastAPI app, CORS, rate limiting, router registration
    parser.py             Deterministic payslip parsing engine
    envelope_engine.py     Rule-based envelope allocation + lifecycle ops
    models.py              SQLAlchemy ORM models
    schemas.py              Pydantic request/response schemas
    database.py            Engine/session config (Postgres or SQLite)
    auth.py                 Password hashing (bcrypt) + JWT issuance/verification
    routers/
      auth.py               /auth/register, /auth/login, /auth/me
      payslips.py            /payslips/parse, /payslips/
      envelopes.py            /envelopes CRUD + lock/archive/merge/split/transfer
      transactions.py          /transactions with filtering
      reports.py                /reports/cash-flow, expense-categories, etc.
  tests/
    test_parser.py
    test_envelope_engine.py
  requirements.txt
```

## Security notes

- Passwords are hashed with bcrypt directly (not via passlib's CryptContext,
  which has known incompatibilities with recent bcrypt releases).
- Raw payslip text is never stored — only a SHA-256 hash, matching the
  product's "purge raw document" privacy commitment.
- JWTs expire after 7 days; set `JWT_SECRET_KEY` in production — the default
  in `auth.py` is for local development only.
