from pymongo import MongoClient
from app.config.settings import settings

client = MongoClient(settings.mongodb_uri)
db = client.eventshub_db

users_collection = db["users"]
events_collection = db["events"]
registrations_collection = db["registrations"]