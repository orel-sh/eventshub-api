from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone
from app.models.models import Registration
from app.config.database import events_collection, registrations_collection
from app.auth.jwt import get_current_user
from app.schemas.schemas import registration_serial
from app.tasks.email_tasks import send_registration_confirmation

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/", status_code=201)
async def register_to_event(
    registration: Registration,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(registration.event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    event = events_collection.find_one({"_id": ObjectId(registration.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check duplicate registration
    if registrations_collection.find_one({"event_id": registration.event_id, "email": registration.email}):
        raise HTTPException(status_code=409, detail="Already registered for this event")

    # Check capacity
    current_count = registrations_collection.count_documents({"event_id": registration.event_id})
    if current_count >= event["max_participants"]:
        raise HTTPException(status_code=409, detail="Event is fully booked")

    reg_dict = registration.model_dump()
    reg_dict["registered_at"] = datetime.now(timezone.utc)
    result = registrations_collection.insert_one(reg_dict)

    # Fire-and-forget email confirmation via Celery
    send_registration_confirmation.delay(
        to_email=registration.email,
        user_name=registration.user_name,
        event_title=event["title"],
        event_date=str(event.get("date", "")),
    )

    return {"message": "Registered successfully", "id": str(result.inserted_id)}


@router.get("/event/{event_id}")
async def get_participants(event_id: str, _: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    participants = [
        registration_serial(r)
        for r in registrations_collection.find({"event_id": event_id})
    ]

    return {
        "event_title":      event["title"],
        "total":            len(participants),
        "max_participants": event["max_participants"],
        "spots_left":       event["max_participants"] - len(participants),
        "participants":     participants,
    }


@router.delete("/{registration_id}")
async def cancel_registration(registration_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(registration_id):
        raise HTTPException(status_code=400, detail="Invalid registration ID")

    reg = registrations_collection.find_one({"_id": ObjectId(registration_id)})
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Users can only cancel their own registrations; admins can cancel any
    if current_user.get("role") != "admin" and reg.get("email") != current_user.get("email"):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this registration")

    registrations_collection.delete_one({"_id": ObjectId(registration_id)})
    return {"message": "Registration cancelled"}
