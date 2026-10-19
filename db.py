"""Connection helper + collection creation with $jsonSchema validation rules."""
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, DESCENDING
import config

# ---------------------------------------------------------------- connection
def get_client():
    return MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)

def get_db():
    return get_client()[config.DB_NAME]

def today_midnight():
    n = datetime.now(timezone.utc)
    return datetime(n.year, n.month, n.day)

# ---------------------------------------------------------- validation rules
GOAL_TYPES = ["weight_loss", "weight_gain", "maintenance"]
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
WORKOUT_TYPES = ["cardio", "strength", "yoga", "running", "cycling"]
ACTIVITY = ["sedentary", "light", "moderate", "active", "very_active"]
DIET_PREF = ["any", "vegetarian", "vegan", "keto", "high_protein"]
BMI_CATS = ["Underweight", "Normal", "Overweight", "Obese"]

def _s(required, props):
    return {"$jsonSchema": {"bsonType": "object", "required": required, "properties": props}}

SCHEMAS = {
    "users": _s(
        ["name", "email", "password_hash", "role", "profile", "created_at"],
        {
            "name": {"bsonType": "string", "minLength": 2, "maxLength": 100},
            "email": {"bsonType": "string", "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$"},
            "password_hash": {"bsonType": "string"},
            "role": {"enum": ["user", "admin"]},
            "created_at": {"bsonType": "date"},
            "profile": {
                "bsonType": "object",
                "required": ["age", "gender", "height_cm", "weight_kg",
                             "goal_weight_kg", "activity_level", "dietary_preference"],
                "properties": {
                    "age": {"bsonType": "int", "minimum": 10, "maximum": 120},
                    "gender": {"enum": ["male", "female", "other"]},
                    "height_cm": {"bsonType": "number", "minimum": 50, "maximum": 260},
                    "weight_kg": {"bsonType": "number", "minimum": 20, "maximum": 400},
                    "goal_weight_kg": {"bsonType": "number", "minimum": 20, "maximum": 400},
                    "activity_level": {"enum": ACTIVITY},
                    "dietary_preference": {"enum": DIET_PREF},
                },
            },
        }),
    "goals": _s(
        ["user_id", "goal_type", "start_weight_kg", "target_weight_kg",
         "daily_calorie_target", "start_date", "status"],
        {
            "user_id": {"bsonType": "objectId"},
            "goal_type": {"enum": GOAL_TYPES},
            "start_weight_kg": {"bsonType": "number", "minimum": 20, "maximum": 400},
            "target_weight_kg": {"bsonType": "number", "minimum": 20, "maximum": 400},
            "daily_calorie_target": {"bsonType": "number", "minimum": 800, "maximum": 6000},
            "workout_frequency_per_week": {"bsonType": "int", "minimum": 0, "maximum": 14},
            "start_date": {"bsonType": "date"},
            "target_date": {"bsonType": "date"},
            "status": {"enum": ["active", "completed", "abandoned"]},
        }),
    "meals": _s(
        ["user_id", "meal_name", "meal_type", "calories", "date"],
        {
            "user_id": {"bsonType": "objectId"},
            "meal_name": {"bsonType": "string", "minLength": 1, "maxLength": 120},
            "meal_type": {"enum": MEAL_TYPES},
            "calories": {"bsonType": "number", "minimum": 0, "maximum": 5000},
            "protein_g": {"bsonType": "number", "minimum": 0},
            "carbs_g": {"bsonType": "number", "minimum": 0},
            "fat_g": {"bsonType": "number", "minimum": 0},
            "date": {"bsonType": "date"},
        }),
    "workouts": _s(
        ["user_id", "title", "workout_type", "duration_minutes", "calories_burned", "date"],
        {
            "user_id": {"bsonType": "objectId"},
            "title": {"bsonType": "string", "minLength": 1},
            "workout_type": {"enum": WORKOUT_TYPES},
            "duration_minutes": {"bsonType": "int", "minimum": 1, "maximum": 600},
            "calories_burned": {"bsonType": "number", "minimum": 0, "maximum": 5000},
            "date": {"bsonType": "date"},
        }),
    "water_intakes": _s(
        ["user_id", "amount_ml", "date"],
        {
            "user_id": {"bsonType": "objectId"},
            "amount_ml": {"bsonType": "int", "minimum": 1, "maximum": 5000},
            "date": {"bsonType": "date"},
        }),
    "progress_logs": _s(
        ["user_id", "weight_kg", "date"],
        {
            "user_id": {"bsonType": "objectId"},
            "weight_kg": {"bsonType": "number", "minimum": 20, "maximum": 400},
            "date": {"bsonType": "date"},
        }),
    "diet_plans": _s(
        ["name", "goal_type", "bmi_categories", "dietary_preference", "daily_calories"],
        {
            "name": {"bsonType": "string", "minLength": 3},
            "goal_type": {"enum": GOAL_TYPES},
            "bmi_categories": {"bsonType": "array", "minItems": 1, "items": {"enum": BMI_CATS}},
            "dietary_preference": {"enum": DIET_PREF},
            "daily_calories": {"bsonType": "number", "minimum": 800, "maximum": 6000},
            "meals_suggestion": {"bsonType": "array", "items": {"bsonType": "string"}},
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
        }),
    "exercises": _s(
        ["name", "category", "muscle_groups", "difficulty", "calories_per_minute"],
        {
            "name": {"bsonType": "string", "minLength": 2},
            "category": {"enum": WORKOUT_TYPES},
            "muscle_groups": {"bsonType": "array", "minItems": 1, "items": {"bsonType": "string"}},
            "difficulty": {"enum": ["beginner", "intermediate", "advanced"]},
            "calories_per_minute": {"bsonType": "number", "minimum": 0, "maximum": 50},
        }),
}

INDEXES = {
    "users": [([("email", ASCENDING)], {"unique": True})],
    "goals": [([("user_id", ASCENDING), ("status", ASCENDING)], {})],
    "meals": [([("user_id", ASCENDING), ("date", DESCENDING)], {})],
    "workouts": [([("user_id", ASCENDING), ("date", DESCENDING)], {})],
    "water_intakes": [([("user_id", ASCENDING), ("date", DESCENDING)], {})],
    "progress_logs": [([("user_id", ASCENDING), ("date", DESCENDING)], {})],
    "diet_plans": [([("goal_type", ASCENDING), ("dietary_preference", ASCENDING)], {})],
    "exercises": [([("name", ASCENDING)], {"unique": True})],
}

def setup_database(db, drop_existing=False):
    """Create every collection with its validator and indexes."""
    existing = db.list_collection_names()
    for name, validator in SCHEMAS.items():
        if name in existing and drop_existing:
            db.drop_collection(name)
            existing.remove(name)
        if name in existing:
            db.command("collMod", name, validator=validator,
                       validationLevel="strict", validationAction="error")
        else:
            db.create_collection(name, validator=validator,
                                 validationLevel="strict", validationAction="error")
        for keys, opts in INDEXES.get(name, []):
            db[name].create_index(keys, **opts)
    return list(SCHEMAS)
