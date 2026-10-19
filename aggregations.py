"""Aggregation pipelines used for FitTrack analytics."""
from datetime import timedelta
from db import today_midnight

# Reusable stages: compute BMI + category from the embedded profile
BMI_STAGES = [
    {"$addFields": {"bmi": {"$round": [{"$divide": [
        "$profile.weight_kg", {"$pow": [{"$divide": ["$profile.height_cm", 100]}, 2]}]}, 1]}}},
    {"$addFields": {"bmi_category": {"$switch": {"branches": [
        {"case": {"$lt": ["$bmi", 18.5]}, "then": "Underweight"},
        {"case": {"$lt": ["$bmi", 25]}, "then": "Normal"},
        {"case": {"$lt": ["$bmi", 30]}, "then": "Overweight"}],
        "default": "Obese"}}}},
]

# 1 ------------------------------------------------ daily calories + macros
def daily_nutrition(db, user_id, days=7):
    start = today_midnight() - timedelta(days=days - 1)
    return list(db.meals.aggregate([
        {"$match": {"user_id": user_id, "date": {"$gte": start}}},
        {"$group": {"_id": "$date", "calories": {"$sum": "$calories"}, "protein_g": {"$sum": "$protein_g"},
                    "carbs_g": {"$sum": "$carbs_g"}, "fat_g": {"$sum": "$fat_g"}, "meals": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}},
                      "calories": 1, "protein_g": 1, "carbs_g": 1, "fat_g": 1, "meals": 1}},
    ]))

# 2 ------------------------------------------------ weekly calorie trend
def weekly_calorie_trend(db, user_id, weeks=6):
    start = today_midnight() - timedelta(weeks=weeks)
    return list(db.meals.aggregate([
        {"$match": {"user_id": user_id, "date": {"$gte": start}}},
        {"$group": {"_id": {"$dateToString": {"format": "%G-W%V", "date": "$date"}},
                    "total_calories": {"$sum": "$calories"}, "days": {"$addToSet": "$date"}}},
        {"$project": {"_id": 0, "week": "$_id", "total_calories": 1,
                      "avg_daily_calories": {"$round": [{"$divide": ["$total_calories", {"$size": "$days"}]}, 0]}}},
        {"$sort": {"week": 1}},
    ]))

# 3 ------------------------------------------------ BMI category distribution
def bmi_category_counts(db):
    return list(db.users.aggregate([
        {"$match": {"role": "user"}}, *BMI_STAGES,
        {"$group": {"_id": "$bmi_category", "users": {"$sum": 1}, "avg_bmi": {"$avg": "$bmi"},
                    "names": {"$push": "$name"}}},
        {"$project": {"_id": 0, "category": "$_id", "users": 1, "names": 1,
                      "avg_bmi": {"$round": ["$avg_bmi", 1]}}},
        {"$sort": {"users": -1}},
    ]))

# 4 ------------------------------------------------ most popular workout types
def popular_workout_types(db, limit=5):
    return list(db.workouts.aggregate([
        {"$group": {"_id": "$workout_type", "sessions": {"$sum": 1},
                    "total_minutes": {"$sum": "$duration_minutes"},
                    "total_burned": {"$sum": "$calories_burned"},
                    "avg_burned": {"$avg": "$calories_burned"}}},
        {"$sort": {"sessions": -1}}, {"$limit": limit},
        {"$project": {"_id": 0, "workout_type": "$_id", "sessions": 1, "total_minutes": 1,
                      "total_burned": 1, "avg_burned": {"$round": ["$avg_burned", 0]}}},
    ]))

# 5 ------------------------------------------------ goal progress (%)
def goal_progress(db, user_id=None):
    match = {"status": "active"}
    if user_id:
        match["user_id"] = user_id
    return list(db.goals.aggregate([
        {"$match": match},
        {"$lookup": {"from": "progress_logs", "let": {"uid": "$user_id"}, "as": "latest",
                     "pipeline": [{"$match": {"$expr": {"$eq": ["$user_id", "$$uid"]}}},
                                  {"$sort": {"date": -1}}, {"$limit": 1}]}},
        {"$unwind": "$latest"},
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$addFields": {"current_weight": "$latest.weight_kg",
                        "total_change": {"$subtract": ["$target_weight_kg", "$start_weight_kg"]},
                        "done_change": {"$subtract": ["$latest.weight_kg", "$start_weight_kg"]}}},
        {"$addFields": {"raw_pct": {"$cond": [{"$eq": ["$total_change", 0]}, 100,
                                              {"$multiply": [{"$divide": ["$done_change", "$total_change"]}, 100]}]}}},
        {"$project": {"_id": 0, "user": "$user.name", "goal_type": 1, "start_weight_kg": 1,
                      "current_weight": 1, "target_weight_kg": 1,
                      "progress_pct": {"$round": [{"$min": [100, {"$max": [0, "$raw_pct"]}]}, 1]}}},
        {"$sort": {"progress_pct": -1}},
    ]))

# 6 ------------------------------------------------ diet plan recommendation
def recommend_diet_plans(db, user_id):
    return list(db.users.aggregate([
        {"$match": {"_id": user_id}}, *BMI_STAGES,
        {"$lookup": {"from": "goals", "let": {"uid": "$_id"}, "as": "goal",
                     "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$user_id", "$$uid"]},
                                                                  {"$eq": ["$status", "active"]}]}}},
                                  {"$limit": 1}]}},
        {"$unwind": "$goal"},
        {"$lookup": {"from": "diet_plans",
                     "let": {"cat": "$bmi_category", "goal": "$goal.goal_type",
                             "pref": "$profile.dietary_preference"}, "as": "plans",
                     "pipeline": [{"$match": {"$expr": {"$and": [
                         {"$eq": ["$goal_type", "$$goal"]},
                         {"$in": ["$$cat", "$bmi_categories"]},
                         {"$in": ["$dietary_preference", ["any", "$$pref"]]}]}}}]}},
        {"$unwind": "$plans"},
        {"$project": {"_id": 0, "user": "$name", "bmi": 1, "bmi_category": 1,
                      "goal": "$goal.goal_type", "preference": "$profile.dietary_preference",
                      "plan": "$plans.name", "daily_calories": "$plans.daily_calories",
                      "suggested_meals": "$plans.meals_suggestion"}},
    ]))

# 7 ------------------------------------------------ dashboard via $facet
def dashboard_summary(db, user_id, days=7):
    start = today_midnight() - timedelta(days=days - 1)
    meals = list(db.meals.aggregate([
        {"$match": {"user_id": user_id, "date": {"$gte": start}}},
        {"$facet": {
            "totals": [{"$group": {"_id": None, "calories": {"$sum": "$calories"}, "protein_g": {"$sum": "$protein_g"},
                                   "carbs_g": {"$sum": "$carbs_g"}, "fat_g": {"$sum": "$fat_g"}}},
                       {"$project": {"_id": 0}}],
            "by_meal_type": [{"$group": {"_id": "$meal_type", "calories": {"$sum": "$calories"}}},
                             {"$sort": {"calories": -1}}],
            "highest_day": [{"$group": {"_id": "$date", "calories": {"$sum": "$calories"}}},
                            {"$sort": {"calories": -1}}, {"$limit": 1}],
        }}]))[0]
    workouts = list(db.workouts.aggregate([
        {"$match": {"user_id": user_id, "date": {"$gte": start}}},
        {"$group": {"_id": None, "sessions": {"$sum": 1}, "minutes": {"$sum": "$duration_minutes"},
                    "calories_burned": {"$sum": "$calories_burned"}}}, {"$project": {"_id": 0}}]))
    water = list(db.water_intakes.aggregate([
        {"$match": {"user_id": user_id, "date": {"$gte": start}}},
        {"$group": {"_id": None, "total_ml": {"$sum": "$amount_ml"}}},
        {"$project": {"_id": 0, "avg_ml_per_day": {"$round": [{"$divide": ["$total_ml", days]}, 0]}}}]))
    return {"period_days": days, "meals": meals, "workouts": workouts[0] if workouts else {},
            "water": water[0] if water else {}}

# 8 ------------------------------------------------ net calories ($unionWith)
def net_calories(db, user_id, days=7):
    start = today_midnight() - timedelta(days=days - 1)
    return list(db.meals.aggregate([
        {"$match": {"user_id": user_id, "date": {"$gte": start}}},
        {"$group": {"_id": "$date", "consumed": {"$sum": "$calories"}, "burned": {"$sum": 0}}},
        {"$unionWith": {"coll": "workouts", "pipeline": [
            {"$match": {"user_id": user_id, "date": {"$gte": start}}},
            {"$group": {"_id": "$date", "consumed": {"$sum": 0}, "burned": {"$sum": "$calories_burned"}}}]}},
        {"$group": {"_id": "$_id", "consumed": {"$sum": "$consumed"}, "burned": {"$sum": "$burned"}}},
        {"$addFields": {"net": {"$subtract": ["$consumed", "$burned"]}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}},
                      "consumed": 1, "burned": 1, "net": 1}},
    ]))

# 9 ------------------------------------------------ admin: platform statistics
def admin_statistics(db):
    return list(db.meals.aggregate([
        {"$group": {"_id": "$user_id", "total_calories": {"$sum": "$calories"},
                    "logged_days": {"$addToSet": "$date"}}},
        {"$lookup": {"from": "users", "localField": "_id", "foreignField": "_id", "as": "u"}},
        {"$unwind": "$u"},
        {"$project": {"_id": 0, "user": "$u.name",
                      "avg_daily_calories": {"$round": [{"$divide": ["$total_calories", {"$size": "$logged_days"}]}, 0]},
                      "days_logged": {"$size": "$logged_days"}}},
        {"$sort": {"avg_daily_calories": -1}},
    ]))
