"""
Seed script: populates MongoDB + Elasticsearch with sample data.
Run: python seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from app.config.database import users_collection, events_collection, registrations_collection
from app.config.elasticsearch import init_es_index, index_event
from app.auth.jwt import hash_password

# ── Clear existing data ───────────────────────────────────────────────────────
print("[Seed] Clearing existing data...")
users_collection.delete_many({})
events_collection.delete_many({})
registrations_collection.delete_many({})

# ── Users ─────────────────────────────────────────────────────────────────────
print("[Seed] Creating users...")
users = [
    {"name": "Orel Shabat",    "email": "orel@example.com",   "password": hash_password("password123"), "role": "admin"},
    {"name": "Dana Cohen",     "email": "dana@example.com",   "password": hash_password("password123"), "role": "user"},
    {"name": "Yossi Levi",     "email": "yossi@example.com",  "password": hash_password("password123"), "role": "user"},
    {"name": "Michal Katz",    "email": "michal@example.com", "password": hash_password("password123"), "role": "user"},
    {"name": "Avi Mizrahi",    "email": "avi@example.com",    "password": hash_password("password123"), "role": "user"},
    {"name": "Noa Peretz",     "email": "noa@example.com",    "password": hash_password("password123"), "role": "user"},
    {"name": "Itay Ben-David", "email": "itay@example.com",   "password": hash_password("password123"), "role": "user"},
    {"name": "Shira Shapiro",  "email": "shira@example.com",  "password": hash_password("password123"), "role": "user"},
    {"name": "Rotem Gross",    "email": "rotem@example.com",  "password": hash_password("password123"), "role": "user"},
    {"name": "Tal Friedman",   "email": "tal@example.com",    "password": hash_password("password123"), "role": "user"},
    {"name": "Ori Nachum",     "email": "ori@example.com",    "password": hash_password("password123"), "role": "user"},
    {"name": "Lihi Bar",       "email": "lihi@example.com",   "password": hash_password("password123"), "role": "user"},
    {"name": "Eitan Goldberg", "email": "eitan@example.com",  "password": hash_password("password123"), "role": "user"},
    {"name": "Maya Stern",     "email": "maya@example.com",   "password": hash_password("password123"), "role": "user"},
    {"name": "Guy Alon",       "email": "guy@example.com",    "password": hash_password("password123"), "role": "user"},
]
user_ids = users_collection.insert_many(users).inserted_ids
print(f"  + {len(user_ids)} users created")

# ── Events ────────────────────────────────────────────────────────────────────
print("[Seed] Creating events...")
events = [
    {
        "title": "Backend Developer Meetup Tel Aviv",
        "description": "Monthly meetup for backend developers. Talks on FastAPI, microservices and system design.",
        "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
        "date": "2026-03-15T18:00:00", "max_participants": 80,
    },
    {
        "title": "GIS & Spatial Data Workshop",
        "description": "Hands-on workshop covering GeoPandas, PostGIS, spatial queries and map visualization.",
        "location": {"city": "Jerusalem", "country": "Israel", "lat": 31.7683, "lng": 35.2137},
        "date": "2026-04-02T10:00:00", "max_participants": 30,
    },
    {
        "title": "Elasticsearch Deep Dive",
        "description": "Advanced Elasticsearch: indexing strategies, aggregations, geo queries and performance tuning.",
        "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
        "date": "2026-04-20T17:30:00", "max_participants": 50,
    },
    {
        "title": "Python & FastAPI Conference",
        "description": "Full day conference on Python backend development, async programming and API design.",
        "location": {"city": "Haifa", "country": "Israel", "lat": 32.7940, "lng": 34.9896},
        "date": "2026-05-10T09:00:00", "max_participants": 150,
    },
    {
        "title": "Berlin Tech Summit",
        "description": "International summit covering cloud architecture, DevOps, and distributed systems.",
        "location": {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lng": 13.4050},
        "date": "2026-06-05T09:00:00", "max_participants": 300,
    },
    {
        "title": "Data Engineering with Python",
        "description": "Practical workshop on ETL pipelines, data cleaning, Pandas and pipeline automation.",
        "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
        "date": "2026-03-28T17:00:00", "max_participants": 60,
    },
    {
        "title": "Docker & Kubernetes Workshop",
        "description": "Hands-on containerization: Docker Compose and intro to Kubernetes for backend developers.",
        "location": {"city": "Ramat Gan", "country": "Israel", "lat": 32.0741, "lng": 34.8137},
        "date": "2026-04-12T10:00:00", "max_participants": 40,
    },
    {
        "title": "MongoDB for Developers",
        "description": "Schema design, aggregation pipelines, indexing strategies and Atlas features.",
        "location": {"city": "Herzliya", "country": "Israel", "lat": 32.1663, "lng": 34.8434},
        "date": "2026-04-25T18:00:00", "max_participants": 45,
    },
    {
        "title": "System Design Bootcamp",
        "description": "Two-day intensive: design scalable systems, handle millions of users, prepare for interviews.",
        "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
        "date": "2026-05-16T09:00:00", "max_participants": 35,
    },
    {
        "title": "Redis & Caching Strategies",
        "description": "Deep dive into Redis: caching patterns, pub/sub, queues and session management.",
        "location": {"city": "Beer Sheva", "country": "Israel", "lat": 31.2529, "lng": 34.7915},
        "date": "2026-05-22T17:30:00", "max_participants": 50,
    },
    {
        "title": "CI/CD with GitHub Actions",
        "description": "Automate your deployment pipeline: testing, building and deploying with GitHub Actions.",
        "location": {"city": "Haifa", "country": "Israel", "lat": 32.7940, "lng": 34.9896},
        "date": "2026-06-01T10:00:00", "max_participants": 55,
    },
    {
        "title": "Amsterdam Python Meetup",
        "description": "Casual evening meetup for Python developers. Lightning talks and networking.",
        "location": {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lng": 4.9041},
        "date": "2026-06-18T19:00:00", "max_participants": 70,
    },
    {
        "title": "Machine Learning for Backend Devs",
        "description": "Intro to ML concepts for software engineers: model serving, APIs and real-world integration.",
        "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
        "date": "2026-07-05T10:00:00", "max_participants": 60,
    },
    {
        "title": "London API Design Summit",
        "description": "Best practices for REST API design, versioning, authentication and documentation.",
        "location": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
        "date": "2026-07-20T09:00:00", "max_participants": 200,
    },
    {
        "title": "Geo Data Hackathon",
        "description": "24-hour hackathon building location-based apps with open geo data. Teams of 3-4.",
        "location": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
        "date": "2026-08-01T09:00:00", "max_participants": 100,
    },
]
event_ids = events_collection.insert_many(events).inserted_ids
print(f"  + {len(event_ids)} events created")

# ── Index in Elasticsearch ────────────────────────────────────────────────────
print("[Seed] Indexing events in Elasticsearch...")
init_es_index()
indexed = 0
for event, eid in zip(events, event_ids):
    try:
        index_event(event, str(eid))
        indexed += 1
    except Exception as e:
        print(f"  x ES failed for '{event['title']}': {e}")
print(f"  + {indexed}/{len(events)} events indexed")

# ── Registrations ─────────────────────────────────────────────────────────────
print("[Seed] Creating registrations...")
now = datetime.now(timezone.utc)
names  = [u["name"]  for u in users]
emails = [u["email"] for u in users]

def reg(event_idx, user_indices):
    return [
        {"event_id": str(event_ids[event_idx]), "user_name": names[i], "email": emails[i], "registered_at": now}
        for i in user_indices
    ]

registrations = (
    reg(0, [1, 2, 3, 4, 5, 6]) +       # Backend Meetup — 6 people
    reg(1, [1, 3, 7, 9]) +              # GIS Workshop — 4 people
    reg(2, [2, 4, 6, 8, 10]) +          # Elasticsearch — 5 people
    reg(3, [1, 2, 3, 4, 5, 6, 7, 8]) +  # FastAPI Conf — 8 people
    reg(5, [9, 11, 13]) +               # Data Engineering — 3 people
    reg(6, [12, 14]) +                  # Docker — 2 people
    reg(7, [2, 5, 8, 11]) +             # MongoDB — 4 people
    reg(8, [1, 3, 6, 9, 12]) +          # System Design — 5 people
    reg(9, [4, 7, 10, 13]) +            # Redis — 4 people
    reg(12, [2, 4, 6, 8, 10, 12]) +     # ML for Devs — 6 people
    reg(14, [1, 3, 5, 7, 9, 11, 13])    # Geo Hackathon — 7 people
)

reg_ids = registrations_collection.insert_many(registrations).inserted_ids
print(f"  + {len(reg_ids)} registrations created")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n[Seed] Done!")
print(f"  Users:         {len(user_ids)}")
print(f"  Events:        {len(event_ids)}")
print(f"  Registrations: {len(reg_ids)}")
print("\nAdmin login:")
print("  email:    orel@example.com")
print("  password: password123")
