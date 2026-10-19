"""Populate the database with realistic sample data (30 days of activity)."""
import random, hashlib, os
from datetime import timedelta, datetime, timezone
from db import get_db, setup_database, today_midnight

random.seed(42)

def hash_pw(pw):
    salt = os.urandom(8).hex()
    return salt + "$" + hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 10_000).hex()

MEALS = {
    "breakfast": [("Oats with banana", 320, 10, 58, 6), ("Veg omelette", 280, 18, 6, 20),
                  ("Poha", 250, 6, 45, 5), ("Idli sambar", 300, 9, 56, 4)],
    "lunch": [("Dal rice", 520, 18, 90, 8), ("Grilled chicken salad", 450, 38, 15, 18),
              ("Paneer wrap", 560, 24, 55, 24), ("Rajma chawal", 580, 20, 95, 9)],
    "dinner": [("Chapati sabzi", 430, 12, 68, 11), ("Fish curry & rice", 520, 34, 60, 14),
               ("Tofu stir fry", 380, 22, 24, 18), ("Veg khichdi", 400, 14, 70, 7)],
    "snack": [("Almonds", 160, 6, 6, 14), ("Greek yogurt", 130, 12, 8, 4),
              ("Protein shake", 200, 25, 10, 4), ("Fruit bowl", 120, 2, 28, 1)],
}
WORKOUT = {"cardio": (35, 9), "strength": (50, 7), "yoga": (45, 4), "running": (30, 11), "cycling": (45, 8)}

USERS = [  # name, email, age, gender, h, w, goal_w, activity, pref, goal_type
    ("Akshat Rana", "user@fittrack.test", 21, "male", 175, 82.0, 74.0, "moderate", "any", "weight_loss"),
    ("Priya Sharma", "priya@fittrack.test", 26, "female", 162, 48.0, 54.0, "light", "vegetarian", "weight_gain"),
    ("Rohan Mehta", "rohan@fittrack.test", 30, "male", 180, 95.0, 85.0, "sedentary", "high_protein", "weight_loss"),
    ("Anita Desai", "anita@fittrack.test", 34, "female", 158, 62.0, 62.0, "active", "vegan", "maintenance"),
    ("Karan Singh", "karan@fittrack.test", 28, "male", 178, 70.0, 76.0, "very_active", "any", "weight_gain"),
    ("Neha Verma", "neha@fittrack.test", 40, "female", 165, 80.0, 70.0, "light", "keto", "weight_loss"),
]

def run():
    db = get_db()
    setup_database(db, drop_existing=True)
    now = datetime.now(timezone.utc)
    today = today_midnight()

    # admin
    db.users.insert_one({
        "name": "Admin", "email": "admin@fittrack.test", "password_hash": hash_pw("password"),
        "role": "admin", "created_at": now,
        "profile": {"age": 35, "gender": "other", "height_cm": 170, "weight_kg": 70.0,
                    "goal_weight_kg": 70.0, "activity_level": "moderate", "dietary_preference": "any"}})

    for name, email, age, g, h, w, gw, act, pref, gtype in USERS:
        uid = db.users.insert_one({
            "name": name, "email": email, "password_hash": hash_pw("password"), "role": "user",
            "created_at": now,
            "profile": {"age": age, "gender": g, "height_cm": h, "weight_kg": w, "goal_weight_kg": gw,
                        "activity_level": act, "dietary_preference": pref}}).inserted_id

        db.goals.insert_one({
            "user_id": uid, "goal_type": gtype, "start_weight_kg": w, "target_weight_kg": gw,
            "daily_calorie_target": {"weight_loss": 1800, "weight_gain": 2800, "maintenance": 2200}[gtype],
            "workout_frequency_per_week": 4, "start_date": today - timedelta(days=30),
            "target_date": today + timedelta(days=90), "status": "active"})

        meals, workouts, water, logs = [], [], [], []
        for d in range(30, -1, -1):
            day = today - timedelta(days=d)
            for mt, options in MEALS.items():
                if mt == "snack" and random.random() < 0.3:
                    continue
                n, c, p, cb, f = random.choice(options)
                meals.append({"user_id": uid, "meal_name": n, "meal_type": mt, "calories": c,
                              "protein_g": p, "carbs_g": cb, "fat_g": f, "date": day})
            if random.random() < 0.6:
                wt = random.choice(list(WORKOUT))
                dur = random.choice([20, 30, 45, 60])
                workouts.append({"user_id": uid, "title": f"{wt.title()} session", "workout_type": wt,
                                 "duration_minutes": dur, "calories_burned": dur * WORKOUT[wt][1],
                                 "date": day})
            for _ in range(random.randint(3, 6)):
                water.append({"user_id": uid, "amount_ml": random.choice([250, 500, 750]), "date": day})
            if d % 3 == 0:  # weight log every 3 days, drifting towards goal
                progress = (30 - d) / 30 * 0.35 * (gw - w)
                logs.append({"user_id": uid, "weight_kg": round(w + progress + random.uniform(-.2, .2), 1),
                             "date": day})
        db.meals.insert_many(meals)
        db.workouts.insert_many(workouts)
        db.water_intakes.insert_many(water)
        db.progress_logs.insert_many(logs)

    db.diet_plans.insert_many([
        {"name": "Weight Loss Diet", "goal_type": "weight_loss", "bmi_categories": ["Overweight", "Obese"],
         "dietary_preference": "any", "daily_calories": 1800,
         "meals_suggestion": ["Oats", "Grilled chicken salad", "Veg soup"], "tags": ["low-calorie"]},
        {"name": "Keto Fat Loss", "goal_type": "weight_loss", "bmi_categories": ["Overweight", "Obese"],
         "dietary_preference": "keto", "daily_calories": 1700,
         "meals_suggestion": ["Egg & avocado", "Paneer tikka"], "tags": ["low-carb"]},
        {"name": "High Protein Cut", "goal_type": "weight_loss", "bmi_categories": ["Overweight", "Normal"],
         "dietary_preference": "high_protein", "daily_calories": 1900,
         "meals_suggestion": ["Chicken breast", "Protein shake"], "tags": ["protein"]},
        {"name": "Muscle Gain Diet", "goal_type": "weight_gain", "bmi_categories": ["Underweight", "Normal"],
         "dietary_preference": "any", "daily_calories": 2900,
         "meals_suggestion": ["Rice & chicken", "Peanut butter toast"], "tags": ["bulk", "protein"]},
        {"name": "Vegetarian Bulk", "goal_type": "weight_gain", "bmi_categories": ["Underweight", "Normal"],
         "dietary_preference": "vegetarian", "daily_calories": 2700,
         "meals_suggestion": ["Paneer paratha", "Dal rice", "Banana shake"], "tags": ["vegetarian"]},
        {"name": "Vegan Plan", "goal_type": "maintenance", "bmi_categories": ["Normal"],
         "dietary_preference": "vegan", "daily_calories": 2100,
         "meals_suggestion": ["Tofu bowl", "Chickpea salad"], "tags": ["vegan", "plant-based"]},
        {"name": "Balanced Maintenance", "goal_type": "maintenance", "bmi_categories": ["Normal", "Overweight"],
         "dietary_preference": "any", "daily_calories": 2200,
         "meals_suggestion": ["Chapati sabzi", "Fruit bowl"], "tags": ["balanced"]},
    ])

    db.exercises.insert_many([
        {"name": "Burpees", "category": "cardio", "muscle_groups": ["full body"], "difficulty": "intermediate", "calories_per_minute": 12},
        {"name": "Jump Rope", "category": "cardio", "muscle_groups": ["calves", "shoulders"], "difficulty": "beginner", "calories_per_minute": 11},
        {"name": "Bench Press", "category": "strength", "muscle_groups": ["chest", "triceps"], "difficulty": "intermediate", "calories_per_minute": 7},
        {"name": "Deadlift", "category": "strength", "muscle_groups": ["back", "hamstrings", "glutes"], "difficulty": "advanced", "calories_per_minute": 8},
        {"name": "Sun Salutation", "category": "yoga", "muscle_groups": ["full body"], "difficulty": "beginner", "calories_per_minute": 4},
        {"name": "Warrior Pose", "category": "yoga", "muscle_groups": ["legs", "core"], "difficulty": "beginner", "calories_per_minute": 3.5},
        {"name": "5K Run", "category": "running", "muscle_groups": ["legs", "core"], "difficulty": "intermediate", "calories_per_minute": 11},
        {"name": "Hill Sprints", "category": "running", "muscle_groups": ["quadriceps", "glutes"], "difficulty": "advanced", "calories_per_minute": 14},
        {"name": "Road Cycling", "category": "cycling", "muscle_groups": ["quadriceps", "calves"], "difficulty": "beginner", "calories_per_minute": 8},
        {"name": "Spin Intervals", "category": "cycling", "muscle_groups": ["legs", "glutes"], "difficulty": "intermediate", "calories_per_minute": 10},
    ])
    print("Seeded:", {c: db[c].count_documents({}) for c in db.list_collection_names()})

if __name__ == "__main__":
    run()
