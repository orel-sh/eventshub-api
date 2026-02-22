"""
ETL Pipeline: Import events from JSON or CSV into MongoDB + Elasticsearch.

Usage:
    python -m app.etl.pipeline --file events.json
    python -m app.etl.pipeline --file events.csv
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from app.config.database import events_collection
from app.config.elasticsearch import index_event, init_es_index


def parse_event(raw: dict) -> dict:
    """Validate and normalize a raw event dict."""
    required = {"title", "description", "city", "country", "lat", "lng", "date", "max_participants"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Missing fields: {missing}")

    return {
        "title":       raw["title"].strip(),
        "description": raw["description"].strip(),
        "location": {
            "city":    raw["city"].strip(),
            "country": raw["country"].strip(),
            "lat":     float(raw["lat"]),
            "lng":     float(raw["lng"]),
        },
        "date":             str(raw["date"]),
        "max_participants": int(raw["max_participants"]),
        "imported_at":      datetime.utcnow().isoformat(),
    }


def load_json(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def load_csv(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_pipeline(filepath: str):
    print(f"[ETL] Loading: {filepath}")

    if filepath.endswith(".json"):
        raw_events = load_json(filepath)
    elif filepath.endswith(".csv"):
        raw_events = load_csv(filepath)
    else:
        print("[ETL] Unsupported file type. Use .json or .csv")
        sys.exit(1)

    print(f"[ETL] Found {len(raw_events)} records")
    init_es_index()

    success, failed = 0, 0

    for i, raw in enumerate(raw_events):
        try:
            event_doc = parse_event(raw)
            result = events_collection.insert_one(event_doc)
            mongo_id = str(result.inserted_id)
            index_event(event_doc, mongo_id)
            success += 1
        except Exception as e:
            print(f"[ETL] Row {i+1} failed: {e}")
            failed += 1

    print(f"\n[ETL] Done — {success} imported, {failed} failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GeoEvents ETL Pipeline")
    parser.add_argument("--file", required=True, help="Path to .json or .csv file")
    args = parser.parse_args()
    run_pipeline(args.file)
