"""Menu-driven demo of the FitTrack MongoDB project (PyMongo)."""
import sys
from bson import json_util
import config, crud, aggregations as agg
from db import get_db, setup_database

def show(title, data):
    print(f"\n=== {title} ===")
    print(json_util.dumps(data, indent=2, default=str) if not isinstance(data, str) else data)

def full_demo(db, user):
    uid = user["_id"]
    print(f"\nDemo user: {user['name']} ({user['email']})")
    # CREATE
    mid = crud.add_meal(db, uid, "Demo Paneer Sandwich", "snack", 350, 18, 30, 15)
    show("CREATE  add_meal -> inserted _id", str(mid))
    show("CREATE  insert_many snacks -> ids", [str(i) for i in crud.add_many_snacks(db, uid)])
    # READ
    show("READ  today's meals (projection)", crud.meals_on_day(db, uid))
    show("READ  5 most recent workouts (sort+limit)", crud.recent_workouts(db, uid))
    show("READ  meals >= 500 kcal ($gte)", crud.high_calorie_meals(db, uid))
    show("READ  diet plans with tag 'protein' (array match)", crud.plans_by_tag(db, "protein"))
    # UPDATE
    show("UPDATE  meal calories 350 -> 400 (modified)", crud.update_meal_calories(db, mid, 400))
    show("UPDATE  profile.weight_kg via dot-notation (modified)", crud.update_weight(db, uid, 81.5))
    show("UPDATE  $inc latest water entry (modified)", crud.add_water_to_latest(db, uid, 250))
    show("UPDATE  $addToSet tag on plan (modified)", crud.tag_diet_plan(db, "Weight Loss Diet", "beginner-friendly"))
    show("UPDATE  $push meal suggestion (modified)", crud.push_meal_suggestion(db, "Weight Loss Diet", "Moong dal chilla"))
    show("UPDATE  update_many snack protein (modified)", crud.bump_all_snack_protein(db, uid))
    # DELETE
    show("DELETE  delete_one demo meal (deleted)", crud.delete_meal(db, mid))
    # VALIDATION
    show("VALIDATION  invalid inserts", [f"{r} -> {s}" for r, s in crud.demo_validation_failures(db, uid)])
    # AGGREGATIONS
    show("AGG 1  daily calories & macros (7 days)", agg.daily_nutrition(db, uid))
    show("AGG 2  weekly calorie trend", agg.weekly_calorie_trend(db, uid))
    show("AGG 3  BMI category distribution", agg.bmi_category_counts(db))
    show("AGG 4  popular workout types", agg.popular_workout_types(db))
    show("AGG 5  goal progress %", agg.goal_progress(db))
    show("AGG 6  diet recommendations for user", agg.recommend_diet_plans(db, uid))
    show("AGG 7  dashboard summary ($facet)", agg.dashboard_summary(db, uid))
    show("AGG 8  net calories ($unionWith)", agg.net_calories(db, uid))
    show("AGG 9  admin statistics", agg.admin_statistics(db))

MENU = """
================ FitTrack (MongoDB) ================
 1  Seed database (drops & recreates collections)
 2  Show validation rules (rejected inserts)
 3  CRUD demo (create/read/update/delete)
 4  Daily calories & macros
 5  Weekly calorie trend
 6  BMI category counts
 7  Popular workout types
 8  Goal progress
 9  Diet recommendations
10  Dashboard summary ($facet)
11  Net calories ($unionWith)
12  Admin statistics
13  Run FULL demo (for screenshots)
 0  Exit
"""

def main():
    db = get_db()
    try:
        db.client.admin.command("ping")
    except Exception as e:
        sys.exit(f"Cannot connect to MongoDB at {config.MONGO_URI}: {e}")
    if "users" not in db.list_collection_names():
        import seed; seed.run()
    user = crud.get_user(db, config.DEMO_USER_EMAIL)
    uid = user["_id"]
    actions = {
        "2": lambda: show("Validation", [f"{r} -> {s}" for r, s in crud.demo_validation_failures(db, uid)]),
        "4": lambda: show("Daily nutrition", agg.daily_nutrition(db, uid)),
        "5": lambda: show("Weekly trend", agg.weekly_calorie_trend(db, uid)),
        "6": lambda: show("BMI categories", agg.bmi_category_counts(db)),
        "7": lambda: show("Workout types", agg.popular_workout_types(db)),
        "8": lambda: show("Goal progress", agg.goal_progress(db)),
        "9": lambda: show("Recommendations", agg.recommend_diet_plans(db, uid)),
        "10": lambda: show("Dashboard", agg.dashboard_summary(db, uid)),
        "11": lambda: show("Net calories", agg.net_calories(db, uid)),
        "12": lambda: show("Admin stats", agg.admin_statistics(db)),
        "13": lambda: full_demo(db, user),
        "3": lambda: full_demo_crud(db, uid),
    }
    while True:
        print(MENU)
        c = input("Choose: ").strip()
        if c == "0":
            break
        if c == "1":
            import seed; seed.run(); user = crud.get_user(db, config.DEMO_USER_EMAIL); uid = user["_id"]
        elif c in actions:
            actions[c]()
        else:
            print("Invalid choice")

def full_demo_crud(db, uid):
    mid = crud.add_meal(db, uid, "Demo Salad", "lunch", 250, 8, 20, 10)
    show("Created meal", str(mid))
    show("Read today's meals", crud.meals_on_day(db, uid))
    show("Updated (modified count)", crud.update_meal_calories(db, mid, 300))
    show("Deleted (deleted count)", crud.delete_meal(db, mid))

if __name__ == "__main__":
    main()
