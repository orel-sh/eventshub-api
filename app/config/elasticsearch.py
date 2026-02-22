from elasticsearch import Elasticsearch
from app.config.settings import settings

es = Elasticsearch(settings.elasticsearch_url)

EVENTS_INDEX = "events"

EVENTS_MAPPING = {
    "mappings": {
        "properties": {
            "title":       {"type": "text"},
            "description": {"type": "text"},
            "city":        {"type": "keyword"},
            "country":     {"type": "keyword"},
            "location":    {"type": "geo_point"},
            "date":        {"type": "date"},
            "max_participants": {"type": "integer"},
            "mongo_id":    {"type": "keyword"},
        }
    }
}


def init_es_index():
    if not es.indices.exists(index=EVENTS_INDEX):
        es.indices.create(index=EVENTS_INDEX, body=EVENTS_MAPPING)


def index_event(event_doc: dict, mongo_id: str):
    es.index(
        index=EVENTS_INDEX,
        id=mongo_id,
        document={
            "title":       event_doc["title"],
            "description": event_doc["description"],
            "city":        event_doc["location"]["city"],
            "country":     event_doc["location"]["country"],
            "location": {
                "lat": event_doc["location"]["lat"],
                "lon": event_doc["location"]["lng"],
            },
            "date":             event_doc["date"],
            "max_participants": event_doc["max_participants"],
            "mongo_id":         mongo_id,
        }
    )


def delete_event_from_es(mongo_id: str):
    try:
        es.delete(index=EVENTS_INDEX, id=mongo_id)
    except Exception:
        pass


def search_events(query: str = None, city: str = None, date_from: str = None, date_to: str = None):
    must = []

    if query:
        must.append({
            "multi_match": {
                "query": query,
                "fields": ["title^2", "description"],
                "fuzziness": "AUTO"
            }
        })

    if city:
        must.append({"term": {"city": city}})

    if date_from or date_to:
        date_range = {}
        if date_from:
            date_range["gte"] = date_from
        if date_to:
            date_range["lte"] = date_to
        must.append({"range": {"date": date_range}})

    body = {"query": {"bool": {"must": must}} if must else {"match_all": {}}}

    result = es.search(index=EVENTS_INDEX, body=body, size=50)
    return [hit["_source"] | {"id": hit["_id"]} for hit in result["hits"]["hits"]]
