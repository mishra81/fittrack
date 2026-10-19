"""Configuration for the FitTrack MongoDB project."""
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "fittrack_db")
DEMO_USER_EMAIL = "user@fittrack.test"   # same demo login as the Laravel app
