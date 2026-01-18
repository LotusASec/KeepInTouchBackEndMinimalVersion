"""Core configuration and settings"""
import os
from typing import Optional

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database Configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./animal_tracking.db")

# Form Generation Configuration
FORM_GEN_INTERVAL_HOURS = float(os.getenv("FORM_GEN_INTERVAL_HOURS", "12"))

# App Metadata
APP_TITLE = "Hayvan Sahiplendirme Takip Sistemi"
APP_DESCRIPTION = "Hayvan sahiplendirme derneği için takip ve form yönetim sistemi"
APP_VERSION = "1.0.0"
