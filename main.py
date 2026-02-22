from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.events import router as events_router
from app.routes.registrations import router as registrations_router
from app.config.elasticsearch import init_es_index

app = FastAPI(
    title="GeoEvents Platform",
    description=(
        "API for managing location-based events. "
        "Features: JWT auth, Elasticsearch search, Redis caching, "
        "Celery background tasks, and ETL pipeline."
    ),
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(registrations_router)


@app.on_event("startup")
async def startup():
    try:
        init_es_index()
    except Exception as e:
        print(f"[Startup] Elasticsearch not ready yet: {e}")


@app.get("/")
async def root():
    return {"message": "GeoEvents Platform is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
