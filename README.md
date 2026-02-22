# GeoEvents Platform

A production-grade REST API for managing location-based events — built with FastAPI, MongoDB, Elasticsearch, Redis, and Celery.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   FastAPI   │────▶│   MongoDB    │     │    Redis    │
│     API     │     │  (storage)   │     │  (cache +   │
│             │────▶│Elasticsearch │     │   broker)   │
│             │────▶│  (search)    │     └──────┬──────┘
└─────────────┘     └──────────────┘            │
                                         ┌──────▼──────┐
                                         │   Celery    │
                                         │  (email bg  │
                                         │    tasks)   │
                                         └─────────────┘
```

## Features

| Feature | Implementation |
|---------|---------------|
| Authentication | JWT (register / login / role-based access) |
| Event search | Elasticsearch — full-text, city filter, date range, fuzzy match |
| Search caching | Redis — 5 min TTL per unique query |
| Email confirmations | Celery background task (fire-and-forget) |
| Data import | ETL pipeline — JSON / CSV → MongoDB + Elasticsearch |
| Tests | pytest with mocked dependencies |
| Containerization | Docker Compose — all services in one command |

## Tech Stack

- **Python 3.11** + **FastAPI**
- **MongoDB** (Atlas or local)
- **Elasticsearch 8**
- **Redis 7**
- **Celery 5**
- **Docker** + **docker-compose**
- **Pydantic v2**, **python-jose**, **passlib**

## Project Structure

```
geoevents-platform/
├── app/
│   ├── auth/          # JWT utilities, password hashing, role guards
│   ├── config/        # MongoDB, Elasticsearch, Redis clients + settings
│   ├── etl/           # ETL pipeline (JSON/CSV → MongoDB + ES)
│   ├── models/        # Pydantic request/response models
│   ├── routes/        # auth, events, registrations
│   ├── schemas/       # MongoDB document serializers
│   ├── tasks/         # Celery tasks (email confirmation)
│   └── tests/         # pytest test suite
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── sample_events.json
```

## Getting Started

### 1. Configure environment

```bash
cp .env.example .env
# Fill in MONGODB_URI, JWT_SECRET, SMTP credentials
```

### 2. Run everything

```bash
docker-compose up --build
```

API: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### 3. Run locally (without Docker)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Import sample data via ETL

```bash
python -m app.etl.pipeline --file sample_events.json
```

### 5. Run tests

```bash
pytest app/tests/ -v
```

## API Reference

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login → returns JWT |
| GET | `/auth/me` | Get current user (auth required) |

### Events

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/events/` | — | List all events |
| GET | `/events/{id}` | — | Get event by ID |
| GET | `/events/search?q=...&city=...&date_from=...` | — | Elasticsearch search |
| POST | `/events/` | Admin | Create event |
| PUT | `/events/{id}` | Admin | Update event |
| DELETE | `/events/{id}` | Admin | Delete event |

### Registrations

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/registrations/` | User | Register to event (sends confirmation email) |
| GET | `/registrations/event/{id}` | User | List participants + capacity info |
| DELETE | `/registrations/{id}` | User/Admin | Cancel registration |

## Example Requests

**Search events:**
```
GET /events/search?q=backend&city=Tel Aviv&date_from=2026-01-01
```

**Register to event:**
```json
POST /registrations/
Authorization: Bearer <token>
{
  "event_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "user_name": "Orel Shabat",
  "email": "orel@example.com"
}
```

**Import events from CSV:**
```bash
python -m app.etl.pipeline --file events.csv
```

CSV format: `title,description,city,country,lat,lng,date,max_participants`
