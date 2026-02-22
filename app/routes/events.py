import json
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from typing import Optional
from app.models.models import Event, EventUpdate
from app.config.database import events_collection
from app.config.elasticsearch import index_event, delete_event_from_es, search_events
from app.config.redis_client import redis_client
from app.auth.jwt import get_current_user, require_admin
from app.schemas.schemas import event_serial

router = APIRouter(prefix="/events", tags=["Events"])

CACHE_TTL = 300  # 5 minutes


@router.get("/search")
async def search(
    query: Optional[str] = Query(None, description="Full-text search"),
    city: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO date e.g. 2026-03-01"),
    date_to: Optional[str] = Query(None),
):
    cache_key = f"search:{query}:{city}:{date_from}:{date_to}"
    cached = redis_client.get(cache_key)
    if cached:
        return {"source": "cache", "results": json.loads(cached)}

    results = search_events(query=query, city=city, date_from=date_from, date_to=date_to)
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(results, default=str))
    return {"source": "elasticsearch", "results": results}


@router.get("/")
async def get_events():
    return [event_serial(e) for e in events_collection.find()]


@router.get("/{event_id}")
async def get_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_serial(event)


@router.post("/", status_code=201)
async def create_event(event: Event, _: dict = Depends(require_admin)):
    event_dict = event.model_dump()
    event_dict["date"] = str(event_dict["date"])
    result = events_collection.insert_one(event_dict)
    mongo_id = str(result.inserted_id)

    # Index in Elasticsearch
    index_event(event_dict, mongo_id)

    return {"message": "Event created", "id": mongo_id}


@router.put("/{event_id}")
async def update_event(event_id: str, event: EventUpdate, _: dict = Depends(require_admin)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    update_data = {k: v for k, v in event.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = events_collection.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    # Re-index updated event
    updated = events_collection.find_one({"_id": ObjectId(event_id)})
    index_event(updated, event_id)

    return {"message": "Event updated"}


@router.delete("/{event_id}")
async def delete_event(event_id: str, _: dict = Depends(require_admin)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    result = events_collection.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    delete_event_from_es(event_id)
    return {"message": "Event deleted"}
