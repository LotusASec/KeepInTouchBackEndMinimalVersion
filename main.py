from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import os
import models
from database import engine, SessionLocal
from routers import user, animal, form

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hayvan Sahiplendirme Takip Sistemi",
    description="Hayvan sahiplendirme derneği için takip ve form yönetim sistemi",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik origin'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(animal.router)
app.include_router(form.router)


# Background scheduler to auto-trigger periodic form creation
scheduler = BackgroundScheduler(timezone="UTC")


def run_periodic_job():
    db = SessionLocal()
    try:
        form.run_periodic_form_generation(db)
    finally:
        db.close()


@app.on_event("startup")
def start_scheduler():
    # Interval configurable via env; default 12 hours
    interval_hours = float(os.getenv("FORM_GEN_INTERVAL_HOURS", "12"))
    scheduler.add_job(run_periodic_job, "interval", hours=interval_hours, max_instances=1, coalesce=True)
    scheduler.start()


@app.on_event("shutdown")
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/")
def root():
    return {
        "message": "Hayvan Sahiplendirme Takip Sistemi API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
