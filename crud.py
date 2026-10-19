"""All CRUD operations (Create, Read, Update, Delete) used in the project."""
from datetime import datetime, timedelta, timezone
from pymongo.errors import WriteError, DuplicateKeyError
from db import today_midnight

# ------------------------------------------------------------------- helpers
def get_user(db, email):
    return db.users.find_one({"email": email})

# ------------------------------------------------------------------- CREATE
def create_user(db, name, email, password_hash, profile, role="user"):
    doc = {"name": name, "email": email, "password_hash": password_hash, "role": role,
           "profile": profile, "created_at": datetime.now(timezone.utc)}
    return db.users.insert_one(doc).inserted_id                     # insert_one

def add_meal(db, user_id, meal_name, meal_type, calories, protein=0, carbs=0, fat=0, date=None):
    return db.meals.insert_one({
        "user_id": user_id, "meal_name": meal_name, "meal_type": meal_type, "calories": calories,
        "protein_g": protein, "carbs_g": carbs, "fat_g": fat,
        "date": date or today_midnight()}).inserted_id

def add_workout(db, user_id, title, workout_type, minutes, burned, date=None):
    return db.workouts.insert_one({
        "user_id": user_id, "title": title, "workout_type": workout_type,
        "duration_minutes": minutes, "calories_burned": burned,
        "date": date or today_midnight()}).inserted_id

def add_water(db, user_id, ml, date=None):
    return db.water_intakes.insert_one(
        {"user_id": user_id, "amount_ml": ml, "date": date or today_midnight()}).inserted_id

def add_weight_log(db, user_id, kg, date=None):
    return db.progress_logs.insert_one(
        {"user_id": user_id, "weight_kg": kg, "date": date or today_midnight()}).inserted_id

def add_many_snacks(db, user_id):
    """insert_many demo."""
    d = today_midnight()
    docs = [{"user_id": user_id, "meal_name": n, "meal_type": "snack", "calories": c,
             "protein_g": p, "carbs_g": 10, "fat_g": 3, "date": d}
            for n, c, p in [("Boiled eggs", 140, 12), ("Sprouts chaat", 150, 9), ("Roasted chana", 120, 7)]]
    return db.meals.insert_many(docs).inserted_ids                  # insert_many

# --------------------------------------------------------------------- READ
def meals_on_day(db, user_id, day=None):
    day = day or today_midnight()
    return list(db.meals.find({"user_id": user_id, "date": day},
                              {"_id": 0, "meal_name": 1, "meal_type": 1, "calories": 1}))  # projection

def recent_workouts(db, user_id, limit=5):
    return list(db.workouts.find({"user_id": user_id}, {"_id": 0, "user_id": 0})
                .sort("date", -1).limit(limit))                       # sort + limit

def high_calorie_meals(db, user_id, min_cal=500):
    return list(db.meals.find({"user_id": user_id, "calories": {"$gte": min_cal}},
                              {"_id": 0, "meal_name": 1, "calories": 1, "date": 1}).limit(10))

def plans_by_tag(db, tag):
    return list(db.diet_plans.find({"tags": tag}, {"_id": 0, "name": 1, "tags": 1}))  # array query

def count_documents(db, collection, query=None):
    return db[collection].count_documents(query or {})

# ------------------------------------------------------------------- UPDATE
def update_meal_calories(db, meal_id, calories):
    return db.meals.update_one({"_id": meal_id}, {"$set": {"calories": calories}}).modified_count

def update_weight(db, user_id, kg):
    return db.users.update_one({"_id": user_id}, {"$set": {"profile.weight_kg": kg}}).modified_count

def add_water_to_latest(db, user_id, extra_ml):
    """$inc on the most recent water entry."""
    last = db.water_intakes.find_one({"user_id": user_id}, sort=[("date", -1)])
    return db.water_intakes.update_one({"_id": last["_id"]}, {"$inc": {"amount_ml": extra_ml}}).modified_count

def tag_diet_plan(db, plan_name, tag):
    return db.diet_plans.update_one({"name": plan_name}, {"$addToSet": {"tags": tag}}).modified_count

def push_meal_suggestion(db, plan_name, suggestion):
    return db.diet_plans.update_one({"name": plan_name}, {"$push": {"meals_suggestion": suggestion}}).modified_count

def bump_all_snack_protein(db, user_id, extra=2):
    """update_many demo."""
    return db.meals.update_many({"user_id": user_id, "meal_type": "snack"},
                                {"$inc": {"protein_g": extra}}).modified_count

def complete_goal(db, user_id):
    return db.goals.update_one({"user_id": user_id, "status": "active"},
                               {"$set": {"status": "completed"}}).modified_count

# ------------------------------------------------------------------- DELETE
def delete_meal(db, meal_id):
    return db.meals.delete_one({"_id": meal_id}).deleted_count

def delete_old_water_logs(db, user_id, days=60):
    cutoff = today_midnight() - timedelta(days=days)
    return db.water_intakes.delete_many({"user_id": user_id, "date": {"$lt": cutoff}}).deleted_count

# ---------------------------------------------------- VALIDATION DEMOS
def demo_validation_failures(db, user_id):
    """Try inserting invalid documents; each one must be rejected by the validator."""
    bad = [
        ("meals", {"user_id": user_id, "meal_name": "Bad meal", "meal_type": "brunch",
                   "calories": 300, "date": today_midnight()}, "meal_type not in enum"),
        ("meals", {"user_id": user_id, "meal_name": "Negative", "meal_type": "lunch",
                   "calories": -50, "date": today_midnight()}, "calories < 0"),
        ("workouts", {"user_id": user_id, "title": "Zero", "workout_type": "yoga",
                      "duration_minutes": 0, "calories_burned": 10, "date": today_midnight()}, "duration < 1"),
        ("progress_logs", {"user_id": user_id, "weight_kg": 5, "date": today_midnight()}, "weight < 20"),
        ("meals", {"meal_name": "No user", "meal_type": "lunch", "calories": 100,
                   "date": today_midnight()}, "missing required user_id"),
    ]
    results = []
    for coll, doc, reason in bad:
        try:
            db[coll].insert_one(doc)
            results.append((reason, "ACCEPTED (unexpected!)"))
        except WriteError as e:
            results.append((reason, f"REJECTED (code {e.code}: Document failed validation)"))
    # duplicate email -> unique index
    try:
        u = db.users.find_one({"_id": user_id})
        db.users.insert_one({k: v for k, v in u.items() if k != "_id"})
        results.append(("duplicate email", "ACCEPTED (unexpected!)"))
    except DuplicateKeyError:
        results.append(("duplicate email", "REJECTED (unique index)"))
    return results
