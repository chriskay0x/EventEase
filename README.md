# EventEase

A two-sided marketplace for planning and booking events — clients search and
book venues, catering, and DJ/entertainment services from verified vendors,
all in one flow. Vendors list their services, manage availability, and get
paid through escrow-backed payments.

Built with **Django** end-to-end (Django Template Language for the frontend —
no separate React/DRF layer) and **PostgreSQL**.

---

## Table of contents

- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Team ownership](#team-ownership)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Running tests](#running-tests)
- [Git workflow](#git-workflow)
- [A note on PostGIS](#a-note-on-postgis)
- [Roadmap status](#roadmap-status)

---

## Tech stack

| Layer | Choice |
| --- | --- |
| Backend | Django 5.x |
| Frontend | Django Template Language (DTL) |
| Database | PostgreSQL 16 |
| Async jobs | Celery + Redis |
| Payments | Stripe Connect (escrow) |
| Local dev | Docker Compose |
| CI | GitHub Actions |

---

## Project structure

```
eventease/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── eventease/            # project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/              # Team 1 — users, vendor profiles, verification
├── listings/               # Team 2 — venue/service listings, search, availability
├── bookings/               # Team 3 — checkout, payments, escrow
├── engagement/          # Team 4 — reviews, admin panel, notifications
├── templates/              # shared base.html, nav, footer
└── static/                    # shared CSS/JS/images
```

Each app under `INSTALLED_APPS` is owned end-to-end (models, views,
templates, migrations) by one team — see below. Cross-app foreign keys use
Django's string reference syntax (e.g. `models.ForeignKey('listings.VenueListing', ...)`)
so apps never import each other's code directly.

---

## Team ownership

| Team | App | Owns | Depends on |
| --- | --- | --- | --- |
| **Team 1** | `accounts` | User auth (client/vendor/admin), OAuth, vendor verification, roles & permissions | — (foundation) |
| **Team 2** | `listings` | Listing creation, search/filter, availability calendar, geolocation | `accounts.VendorProfile` |
| **Team 3** | `bookings` | Checkout, Stripe Connect escrow payments, concurrency-safe booking | `accounts.User`, `listings` models |
| **Team 4** | `engagement` | Reviews, admin panel, KPI dashboard, Celery notifications | `accounts.User`, `bookings.Booking` |

Don't edit another team's `models.py` or `urls.py` — flag needed changes to
that team's lead instead.

---

## Getting started

### Prerequisites

- Python 3.11+
- Docker Desktop (running)
- Git

### 1. Clone and set up a virtual environment

```bash
git clone <repo-url>
cd eventease

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Adjust values in `.env` if needed — the defaults match `docker-compose.yml`
and work out of the box for local development.

### 3. Start the database

```bash
docker compose up -d
```

This starts a PostgreSQL 16 container matching the credentials in `.env`.
No local Postgres installation needed.

### 4. Run migrations and create an admin user

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the dev server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` — Django admin is at `/admin/`.

---

## Environment variables

Defined in `.env` (see `.env.example` for the full list):

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django's cryptographic signing key — generate a real one for anything beyond local dev |
| `DEBUG` | `True` locally, `False` in staging/production |
| `ALLOWED_HOSTS` | Comma-separated hostnames Django will serve |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection — match `docker-compose.yml` locally |
| `CELERY_BROKER_URL` | Redis URL for background jobs (notifications, reminders) |
| `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Stripe Connect — use test-mode keys locally |

Never commit `.env` — it's gitignored. Only `.env.example` (with placeholder
values) is tracked.

---

## Running tests

```bash
python manage.py test
```

Each team owns test coverage for their own app. CI runs the full suite
(`migrate` + `test`) against a real Postgres service container on every pull
request — a PR that doesn't pass is blocked from merging into `main`.

---

## Git workflow

- `main` is protected — no direct pushes, merges only via reviewed pull
  request.
- One branch per team: `team-1-accounts`, `team-2-listings`,
  `team-3-bookings`, `team-4-engagement`.
- Work only inside your own app's folder.
- Merge to `main` at least 2-3 times a week in small PRs — don't wait until
  a whole feature is "done" to merge; that's what causes big merge
  conflicts.
- If two people on the same team both add a migration off the same base,
  Django will show two files with the same number (e.g. two `0003_*.py`).
  Fix with `python manage.py makemigrations --merge`, or rebase and
  regenerate before opening the PR.
- Weekly 15-minute lead sync across all 4 teams — not a status meeting,
  specifically to flag upcoming changes to a model another team's app
  depends on.
- "Integration day" every 2 sprints: all branches merged and up to date,
  whole team manually walks the full flow — search → view listing → book →
  pay → vendor confirms → review — together, end to end.

---

## A note on PostGIS

`listings` will eventually use PostGIS for real geospatial "near me" search
(`django.contrib.gis.db.models.PointField`), but this is **not enabled yet**.
Setting it up requires GDAL installed at the OS level, which is a real
install headache on some machines and isn't needed for Sprint 0 or early
listings work.

Right now:

- `DATABASES` in `settings.py` uses the plain `django.db.backends.postgresql`
  engine, not the PostGIS backend.
- `django.contrib.gis` is commented out of `INSTALLED_APPS`.
- `docker-compose.yml` uses the plain `postgres:16` image, not
  `postgis/postgis`.
- `VenueListing.latitude` / `longitude` are plain `DecimalField`s as a
  placeholder.

**Team 2**, when you get to the geosearch feature (Sprint 2 of the
implementation plan): switch the Docker image to `postgis/postgis:16-3.4`,
switch the `DATABASES` engine to `django.contrib.gis.db.backends.postgis`,
uncomment `django.contrib.gis` in `INSTALLED_APPS`, install GDAL locally
(`brew install gdal` / `apt install gdal-bin libgdal-dev` — or just rely on
the Docker image, which doesn't need host GDAL for the *database* side,
only for Django's Python GIS libraries), and swap the lat/lng fields for a
real `PointField`.

---

## Roadmap status

- [x] PRD locked (MVP scope: venue, catering, DJ categories only — decor,
  ushers, in-app messaging, and multi-vendor cart are Phase 2)
- [x] Team split and DB ownership agreed
- [x] Git branching workflow agreed
- [x] Core project skeleton + custom `User` model merged to `main`
- [ ] Team 1 — auth & vendor verification
- [ ] Team 2 — listings, search, availability
- [ ] Team 3 — booking, payments, escrow
- [ ] Team 4 — reviews, admin panel, notifications
- [ ] Integration testing & UAT
- [ ] Launch

See the full implementation plan doc for the sprint-by-sprint breakdown per
team and the risk register.
