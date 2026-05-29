# 🍽️ SecondPlate — Surplus Food Rescue & Prediction Platform

> Every day restaurants, canteens, hostels and event venues throw away edible
> surplus food while people nearby go hungry. **SecondPlate** connects food
> **donors** with **recipients** (NGOs, shelters, community kitchens) to rescue
> surplus before it spoils — and uses a real ML model to **forecast tomorrow's
> surplus** so volunteers can be arranged *before* food is cooked to waste.

A full-stack, deployable portfolio project: FastAPI + PostgreSQL backend with a
clean layered architecture, genuine SQL-based impact analytics, a real
(explainable) scikit-learn forecasting model, and a polished React + Tailwind
frontend.

---

## 🟢 Live demo

- **Web app:** <https://secondplate-pi.vercel.app>
- **API + Swagger docs:** <https://secondplate-api.onrender.com/docs>

> Hosted free on Vercel (frontend) + Render (API + PostgreSQL). The API sleeps
> after ~15 min idle, so the **first load after a quiet spell shows skeleton
> loaders for ~30–60s** while it wakes — then real data fills in.

---

## 🚀 Quick start (Docker)

```bash
git clone <your-fork-url> secondplate && cd secondplate
docker compose up --build
```

That's it. Compose will:

1. start **PostgreSQL 15**,
2. run **Alembic migrations**,
3. **seed** ~14 months of signal-rich synthetic data (only if the DB is empty),
4. **train** the surplus model, and
5. serve the API and the web app.

Then open:

| What | URL |
| --- | --- |
| 🖥️  Web app | <http://localhost:8080> |
| 📚  API docs (Swagger) | <http://localhost:8000/docs> |
| ❤️  Health check | <http://localhost:8000/health> |

> First boot takes ~1–2 min (image build + seed + train). The API has a
> healthcheck, so the frontend waits until it is ready.

---

## 🧭 Product tour

- **Browse Rescues** — card grid of available listings, each with a live
  freshness-urgency badge (🟢 fresh / 🟡 expiring soon / 🔴 critical), a ticking
  countdown, donor, distance, and one-click **Claim pickup**.
- **Map** — react-leaflet + OpenStreetMap with urgency-coloured pins; click a
  pin to claim.
- **Impact** — meals rescued, kg of food saved, CO₂e avoided and people served
  (with period-over-period deltas), plus rescues-over-time, food-by-category and
  top-donor charts.
- **Predictions** — per-donor next-day surplus forecast with a confidence score
  and a **"Why?"** drawer showing exactly which features drove each prediction.
- **My Listings** — donor view to post a new listing (validated form) and track
  the status of past donations.
- Toggle **"I'm a Recipient" / "I'm a Donor"** in the top bar to demo both
  sides; light/dark themes; fully responsive.

### Screenshots

_Add images under `docs/screenshots/` and they'll render here._

| Browse | Impact | Predictions |
| --- | --- | --- |
| ![Browse](docs/screenshots/browse.png) | ![Impact](docs/screenshots/impact.png) | ![Predictions](docs/screenshots/predictions.png) |

---

## 🏗️ Architecture

```
                         ┌──────────────────────────────────────┐
                         │             Browser (SPA)             │
                         │  React 18 · Vite · TS · Tailwind ·     │
                         │  shadcn/ui · Recharts · react-leaflet  │
                         └───────────────┬────────────────────────┘
                                         │  HTTP (TanStack Query / axios)
                                         │  /api/*  ·  /health
                         ┌───────────────▼────────────────────────┐
                         │              FastAPI API                │
                         │                                         │
                         │  routers/   thin HTTP endpoints         │
                         │  schemas/   Pydantic v2 (req/resp)      │
                         │  services/  business logic              │
                         │     • geo (haversine)                   │
                         │     • urgency (freshness score)         │
                         │     • impact (SQL aggregation)          │
                         │     • matching (proximity)              │
                         │  ml/        train · predict · explain   │
                         │  models/    SQLAlchemy 2.0 ORM          │
                         └──────┬───────────────────────┬──────────┘
                                │ SQLAlchemy            │ joblib
                         ┌──────▼─────────┐     ┌────────▼─────────┐
                         │  PostgreSQL 15 │     │  surplus_model   │
                         │  (Alembic)     │     │  .joblib + meta  │
                         └────────────────┘     └──────────────────┘
```

The same code runs on **PostgreSQL** (Docker / Render) or **SQLite** (zero-setup
local dev) — only `DATABASE_URL` changes. See
[Notable engineering decisions](#-notable-engineering-decisions).

---

## 🧱 Tech stack

| Layer | Choice |
| --- | --- |
| Backend | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Uvicorn |
| Database | PostgreSQL 15 (SQLite-compatible for local dev) |
| ML / data | scikit-learn (GradientBoostingRegressor), pandas, NumPy, joblib |
| Seeding | Faker |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui-style components, TanStack Query, Recharts, react-leaflet, lucide-react |
| Deploy | Docker + docker-compose · Render (API + Postgres) · Vercel (frontend) |

---

## 📂 Repository layout

```
.
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app: CORS, routers, error handlers, startup
│   │   ├── core/              # config (pydantic-settings), errors, time helpers
│   │   ├── db/                # engine/session, declarative base, UTCDateTime type
│   │   ├── models/            # SQLAlchemy ORM models + enums
│   │   ├── schemas/           # Pydantic v2 request/response models
│   │   ├── routers/           # thin endpoints (listings, impact, predictions, ml, meta)
│   │   ├── services/          # geo, urgency, listings, impact (SQL agg), matching
│   │   ├── ml/                # features, train, predict, model_store
│   │   └── seed/              # Faker seeder with real signal
│   ├── alembic/               # migrations
│   ├── Dockerfile · entrypoint.sh · requirements.txt · .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # ui/ primitives, layout, listings, impact, predictions, map
│   │   ├── pages/             # Browse, Map, Impact, Predictions, MyListings
│   │   ├── lib/               # api client, types, queries, formatters
│   │   ├── state/             # theme + app-state (role/identity/location) contexts
│   │   └── hooks/             # useCountdown
│   ├── Dockerfile · nginx.conf · .env.example
└── docker-compose.yml
```

---

## 🗄️ Database schema

Normalised, with foreign keys, check constraints, indexes and enum-typed columns.

```
        donors                          recipients
   ┌──────────────────┐            ┌─────────────────────┐
   │ id (PK)          │            │ id (PK)             │
   │ name             │            │ name                │
   │ type  [enum]     │            │ type  [enum]        │
   │ lat, lng         │            │ lat, lng            │
   │ address          │            │ capacity            │
   │ created_at       │            │ created_at          │
   └───┬──────────┬───┘            └──────────┬──────────┘
       │1        1│                           │1
       │          │                           │
       │N         │N                          │N
 ┌─────▼──────┐ ┌─▼───────────────┐     ┌─────▼───────────┐
 │ donation_  │ │  food_listings  │     │    pickups      │
 │  history   │ ├─────────────────┤     ├─────────────────┤
 ├────────────┤ │ id (PK)         │1   1│ id (PK)         │
 │ id (PK)    │ │ donor_id (FK)   ├─────┤ listing_id (FK) │
 │ donor_id FK│ │ food_type       │     │ recipient_id FK │
 │ date       │ │ category [enum] │     │ scheduled_at    │
 │ servings_  │ │ servings        │     │ completed_at    │
 │  donated   │ │ prepared_at     │     │ servings_       │
 │ category   │ │ expires_at      │     │  rescued        │
 └────────────┘ │ status   [enum] │     └────────┬────────┘
   (feeds ML)   │ lat, lng        │              │1
                └─────────────────┘              │1
                                          ┌──────▼──────────┐
                                          │   impact_log    │
                                          ├─────────────────┤
                                          │ id (PK)         │
                                          │ pickup_id (FK)  │
                                          │ kg_saved        │
                                          │ co2e_kg         │
                                          │ people_served   │
                                          └─────────────────┘
```

**Enums** — `donor.type` (restaurant/canteen/hostel/event), `recipient.type`
(ngo/shelter/community_kitchen), `food.category`
(cooked/bakery/produce/packaged), `listing.status`
(available/claimed/picked_up/expired).

**Constraints** — `servings > 0`, `expires_at > prepared_at`,
`servings_rescued > 0`, non-negative impact values; a listing has at most one
pickup (unique FK).

**Indexes** — `(status, expires_at)` and `(donor_id, status)` on listings (the
browse hot-path), `(donor_id, date)` on donation history, plus FK indexes.

### Seeded data (with *real* signal)

`app/seed/seed.py` (Faker) generates ~40 donors, 15 recipients and ~14 months of
daily `donation_history`, then hundreds of completed pickups + impact rows and a
set of live listings. Daily surplus is built from interpretable components so the
model has genuine structure to learn:

```
servings = base[type, donor]
         × day_of_week_factor[type][weekday]   # restaurants peak on weekends; canteens on weekdays
         × seasonal_factor(date)               # smooth annual curve, festival-season peak
         × (1 + annual_trend × elapsed)         # slow per-donor drift
         × holiday_factor(date)                 # learnable festival surge (shared calendar with the model)
         × random_event × noise                 # the irreducible part
```

---

## 📊 Impact analysis (how the numbers are computed)

`services/impact_service.py` uses **SQL aggregation** (`GROUP BY` / `SUM`) over
completed pickups joined to their impact rows:

- **Meals rescued** = Σ `servings_rescued`
- **Food saved** = Σ `kg_saved`, where `kg = servings × 0.45`
- **CO₂e avoided** = Σ `co2e_kg`, where `co2e = kg × 2.5` (production + disposal footprint)
- **People served** = Σ `people_served`, where `people ≈ servings × 0.75`
- **Deltas** compare the current window to the immediately preceding one.

Trends return a daily time series (dialect-aware day bucket so it's portable
across SQLite/Postgres), a per-category breakdown and a top-donors ranking.

---

## 🤖 The ML model

**Goal:** predict each donor's **next-day surplus (servings)** so recipients and
volunteers can be arranged ahead of time.

**Model:** `GradientBoostingRegressor` (scikit-learn). Trains in seconds, no
API keys, fully self-contained.

**Features** (`app/ml/features.py`) — per donor/day, all lag/rolling features
shifted to avoid target leakage:

`is_restaurant`, `is_canteen`, `is_hostel`, `is_event`, `day_of_week`,
`is_weekend`, `month`, `is_holiday`, `lag1` (yesterday), `lag7` (same day last
week), `roll7`, `roll30`, `trend` (7d vs 30d).

**Training** (`app/ml/train.py`) — a **temporal** split (earliest 80% train,
latest 20% test — the honest setup for forecasting). Reported on the held-out
tail:

| Metric | Value (typical) |
| --- | --- |
| MAE | ≈ 5.8 servings |
| RMSE | ≈ 9.2 servings |
| R² | ≈ 0.81 |

`POST /api/ml/retrain` retrains on current data and returns live metrics.
`lag7` dominates feature importance (strong weekly seasonality), with
`roll30`, `is_holiday` and `day_of_week` also contributing — i.e. the model is
recovering the signal the seeder injected.

**Explainability** (`app/ml/predict.py`) — global `feature_importances_` plus a
**per-donor local attribution** computed by one-at-a-time ablation: each
feature is replaced with its training mean and we measure how the prediction
moves. This needs no extra dependency (no SHAP) and is exact and intuitive —
it's what the **"Why?"** drawer shows.

**Confidence** — derived transparently from the donor's recent volatility
(lower coefficient of variation over the last 30 days → higher confidence).

### Freshness-urgency score (rule-based, explainable by design)

`services/urgency.py` ranks listings without a model:

```
score = 100 × clip( 0.65·time_pressure + 0.20·perishability + 0.15·size_pressure )
```

`time_pressure` ramps 0→1 as a listing nears expiry over a category-specific
horizon (cooked food gets urgent fastest). Score thresholds map to the
🟢 fresh / 🟡 expiring-soon / 🔴 critical badge.

---

## 🔌 API reference

Base path `/api`. Full interactive docs at `/docs`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Service health + whether the model is loaded |
| `GET` | `/api/donors` | List donors |
| `GET` | `/api/recipients` | List recipients |
| `POST` | `/api/listings` | Donor posts a surplus listing |
| `GET` | `/api/listings?lat&lng&radius&status&category&limit` | Browse listings, sorted by urgency then distance |
| `GET` | `/api/listings/{id}` | Listing detail |
| `GET` | `/api/listings/donor/{donor_id}` | A donor's listings (My Listings) |
| `POST` | `/api/listings/{id}/claim` | Recipient claims a listing (creates a pickup) |
| `GET` | `/api/impact/summary?window_days` | KPIs (meals, kg, CO₂e, people) + deltas |
| `GET` | `/api/impact/trends?range` | Time series + category & donor breakdowns |
| `GET` | `/api/predictions/surplus` | Per-donor next-day forecast + confidence + top factors |
| `GET` | `/api/predictions/{donor_id}/explain` | Full feature attribution for one donor |
| `POST` | `/api/ml/retrain` | Retrain on current data, return MAE/RMSE/R² |

Errors use a consistent shape: `{ "detail": "..." }` (422 for validation).

---

## 💻 Local development (without Docker)

The app defaults to **SQLite**, so no database install is required.

**Backend**

```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate      # Windows
# source .venv/bin/activate                            # macOS/Linux
pip install -r requirements.txt

alembic upgrade head            # create tables (SQLite ./local.db by default)
python -m app.seed.seed         # seed synthetic data
python -m app.ml.train          # train + persist the model
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

**Frontend**

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173 (proxies /api -> :8000)
```

---

## ⚙️ Configuration

**Backend** (`backend/.env.example`)

| Var | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./local.db` | Use `postgresql+psycopg2://…` in prod |
| `CORS_ORIGINS` | `http://localhost:5173,…` | Comma-separated |
| `MODEL_DIR` | `app/ml/artifacts` | Where the model is serialised |
| `ENVIRONMENT` | `development` | |

**Frontend** (`frontend/.env.example`)

| Var | Default | Notes |
| --- | --- | --- |
| `VITE_API_BASE` | _(empty)_ | Empty = dev proxy; set to the API URL in production |

---

## ☁️ Deploy

### Backend + database → Render

**Recommended — Blueprint (one step):** in Render, **New → Blueprint**, select
this repo and click **Apply**. [`render.yaml`](render.yaml) provisions the
Postgres database *and* the API together and injects `DATABASE_URL`
automatically — nothing to copy/paste. Then jump to the Vercel section.

**Manual alternative:**

1. **Create a PostgreSQL instance** (Render → New → PostgreSQL). Copy its
   *Internal Database URL*.
2. **Create a Web Service** from this repo:
   - Root directory: `backend`
   - Environment: **Docker** (uses `backend/Dockerfile`), or Python with
     Build `pip install -r requirements.txt` and Start
     `./entrypoint.sh`.
   - Env vars:
     - `DATABASE_URL` = the Render Postgres URL, with the driver prefix
       `postgresql+psycopg2://…`
     - `CORS_ORIGINS` = your Vercel URL, e.g. `https://secondplate.vercel.app`
     - `ENVIRONMENT` = `production`
3. On deploy, `entrypoint.sh` migrates, seeds (if empty), trains, and serves.
   Health check path: `/health`.

### Frontend → Vercel

1. **Import the repo** in Vercel.
   - Root directory: `frontend`
   - Framework preset: **Vite** · Build: `npm run build` · Output: `dist`
2. Env var: `VITE_API_BASE` = your Render API URL
   (e.g. `https://secondplate-api.onrender.com`).
3. Deploy. CORS for `*.vercel.app` is already allowed via `CORS_ORIGIN_REGEX`
   (set in `render.yaml`), so there's nothing else to wire up.

### Keeping the free API warm (optional)

Render's free tier sleeps after ~15 min idle. The repo includes a GitHub Actions
workflow ([`.github/workflows/keep-alive.yml`](.github/workflows/keep-alive.yml))
that pings `/health` every ~10 minutes to keep it responsive during demos.

- It runs automatically once the repo is on GitHub (check the **Actions** tab and
  enable workflows if prompted). **Disable it when you don't need it** — keeping a
  free instance always awake consumes your free-tier hours.
- GitHub's scheduled runs can be delayed by several minutes; for rock-solid
  uptime use a dedicated pinger like **UptimeRobot** (free, 5-min interval)
  against `https://secondplate-api.onrender.com/health`.

---

## 🧠 Notable engineering decisions

- **One codebase, two databases.** Everything is `DATABASE_URL`-driven via
  pydantic-settings. Production/Docker/Render use **PostgreSQL**; local dev can
  use **SQLite** with zero setup. This made the whole stack runnable and
  testable anywhere without substituting the locked production target.
- **`native_enum=False` enums** (VARCHAR + CHECK) rather than native PG enum
  types — identical behaviour on SQLite and Postgres, no migration foot-guns
  when an enum is reused across tables, and easier evolution. Allowed values are
  still enforced at the DB level.
- **`UTCDateTime` type decorator** guarantees timezone-aware UTC at the API
  boundary on both backends, so client-side countdowns never misparse naive
  timestamps.
- **Layered backend** — routers orchestrate, services hold logic, schemas
  validate; ORM objects are never returned raw.
- **Explainability without SHAP** — exact one-at-a-time ablation against
  training means keeps the dependency surface small and the explanation
  intuitive.

---

## 📜 License

MIT — synthetic data only; conversion factors are reasonable public estimates
for demonstration, not audited figures.
