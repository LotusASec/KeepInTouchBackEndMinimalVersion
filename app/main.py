"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, FORM_GEN_INTERVAL_HOURS
from app.db.database import engine, SessionLocal, Base
from app.api.routers import user, animal, form

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
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
    """Run periodic form generation task"""
    db = SessionLocal()
    try:
        form.run_periodic_form_generation(db)
    finally:
        db.close()


@app.on_event("startup")
def start_scheduler():
    """Start background scheduler on application startup"""
    scheduler.add_job(
        run_periodic_job,
        "interval",
        hours=FORM_GEN_INTERVAL_HOURS,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()


@app.on_event("shutdown")
def stop_scheduler():
    """Stop background scheduler on application shutdown"""
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Hayvan Sahiplendirme Takip Sistemi API",
        "version": APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
