from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Location(BaseModel):
    city: str
    country: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class Event(BaseModel):
    title: str
    description: str
    location: Location
    date: datetime
    max_participants: int = Field(..., gt=0)


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Location] = None
    date: Optional[datetime] = None
    max_participants: Optional[int] = Field(default=None, gt=0)


class Registration(BaseModel):
    event_id: str
    email: EmailStr
    user_name: str
