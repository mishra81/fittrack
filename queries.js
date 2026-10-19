// FitTrack - equivalent mongosh queries.  Run:  mongosh fittrack_db queries.js   (or paste into mongosh)
use("fittrack_db");
const uid = db.users.findOne({ email: "user@fittrack.test" })._id;
const today = new Date(new Date().setUTCHours(0, 0, 0, 0));

// ---------- VALIDATION (example: meals) ----------
db.runCommand({
  collMod: "meals", validationLevel: "strict", validationAction: "error",
  validator: { $jsonSchema: {
    bsonType: "object", required: ["user_id", "meal_name", "meal_type", "calories", "date"],
    properties: {
      user_id: { bsonType: "objectId" },
      meal_name: { bsonType: "string", minLength: 1 },
      meal_type: { enum: ["breakfast", "lunch", "dinner", "snack"] },
      calories: { bsonType: "number", minimum: 0, maximum: 5000 },
      date: { bsonType: "date" } } } }
});
// this fails validation:
try { db.meals.insertOne({ user_id: uid, meal_name: "X", meal_type: "brunch", calories: -5, date: today }); }
catch (e) { print("Rejected: " + e.message); }

// ---------- CREATE ----------
db.meals.insertOne({ user_id: uid, meal_name: "Veg Sandwich", meal_type: "snack", calories: 300,
                     protein_g: 12, carbs_g: 40, fat_g: 9, date: today });
db.water_intakes.insertMany([{ user_id: uid, amount_ml: 250, date: today }, { user_id: uid, amount_ml: 500, date: today }]);

// ---------- READ ----------
db.meals.find({ user_id: uid, date: today }, { _id: 0, meal_name: 1, calories: 1 });
db.workouts.find({ user_id: uid }).sort({ date: -1 }).limit(5);
db.meals.find({ user_id: uid, calories: { $gte: 500 } });
db.diet_plans.find({ tags: "protein" });

// ---------- UPDATE ----------
db.meals.updateOne({ meal_name: "Veg Sandwich", user_id: uid }, { $set: { calories: 320 } });
db.users.updateOne({ _id: uid }, { $set: { "profile.weight_kg": 81.5 } });
db.diet_plans.updateOne({ name: "Weight Loss Diet" }, { $addToSet: { tags: "beginner-friendly" } });
db.diet_plans.updateOne({ name: "Weight Loss Diet" }, { $push: { meals_suggestion: "Moong dal chilla" } });
db.meals.updateMany({ user_id: uid, meal_type: "snack" }, { $inc: { protein_g: 2 } });

// ---------- DELETE ----------
db.meals.deleteOne({ user_id: uid, meal_name: "Veg Sandwich" });
db.water_intakes.deleteMany({ user_id: uid, date: { $lt: new Date(Date.now() - 60 * 864e5) } });

// ---------- AGGREGATIONS ----------
// 1. Daily calories & macros
db.meals.aggregate([
  { $match: { user_id: uid, date: { $gte: new Date(Date.now() - 7 * 864e5) } } },
  { $group: { _id: "$date", calories: { $sum: "$calories" }, protein: { $sum: "$protein_g" },
              carbs: { $sum: "$carbs_g" }, fat: { $sum: "$fat_g" } } },
  { $sort: { _id: 1 } }]);

// 2. Weekly calorie trend
db.meals.aggregate([
  { $match: { user_id: uid } },
  { $group: { _id: { $dateToString: { format: "%G-W%V", date: "$date" } },
              total: { $sum: "$calories" }, days: { $addToSet: "$date" } } },
  { $project: { week: "$_id", avg_daily: { $round: [{ $divide: ["$total", { $size: "$days" }] }, 0] } } },
  { $sort: { week: 1 } }]);

// 3. BMI categories
db.users.aggregate([
  { $match: { role: "user" } },
  { $addFields: { bmi: { $round: [{ $divide: ["$profile.weight_kg", { $pow: [{ $divide: ["$profile.height_cm", 100] }, 2] }] }, 1] } } },
  { $addFields: { category: { $switch: { branches: [
      { case: { $lt: ["$bmi", 18.5] }, then: "Underweight" },
      { case: { $lt: ["$bmi", 25] }, then: "Normal" },
      { case: { $lt: ["$bmi", 30] }, then: "Overweight" }], default: "Obese" } } } },
  { $group: { _id: "$category", users: { $sum: 1 } } }]);

// 4. Popular workout types
db.workouts.aggregate([
  { $group: { _id: "$workout_type", sessions: { $sum: 1 }, burned: { $sum: "$calories_burned" } } },
  { $sort: { sessions: -1 } }, { $limit: 5 }]);

// 5. Goal progress (%) with $lookup
db.goals.aggregate([
  { $match: { status: "active" } },
  { $lookup: { from: "progress_logs", let: { uid: "$user_id" }, as: "latest",
      pipeline: [{ $match: { $expr: { $eq: ["$user_id", "$$uid"] } } }, { $sort: { date: -1 } }, { $limit: 1 }] } },
  { $unwind: "$latest" },
  { $project: { goal_type: 1, start_weight_kg: 1, target_weight_kg: 1, current: "$latest.weight_kg",
      pct: { $round: [{ $multiply: [{ $divide: [{ $subtract: ["$latest.weight_kg", "$start_weight_kg"] },
                                                 { $subtract: ["$target_weight_kg", "$start_weight_kg"] }] }, 100] }, 1] } } }]);

// 7. Dashboard with $facet
db.meals.aggregate([
  { $match: { user_id: uid, date: { $gte: new Date(Date.now() - 7 * 864e5) } } },
  { $facet: {
      totals: [{ $group: { _id: null, calories: { $sum: "$calories" } } }],
      by_meal_type: [{ $group: { _id: "$meal_type", calories: { $sum: "$calories" } } }],
      highest_day: [{ $group: { _id: "$date", c: { $sum: "$calories" } } }, { $sort: { c: -1 } }, { $limit: 1 }] } }]);
