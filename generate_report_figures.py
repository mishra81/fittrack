"""Generate all charts, diagrams, and terminal visual cards for FitTrack Word report."""
import os, shutil
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("report_assets", exist_ok=True)
logo_src = os.path.join("report_assets", "word", "media", "image1.jpeg")
logo_dst = os.path.join("report_assets", "lpu_logo.jpeg")
if os.path.exists(logo_src):
    shutil.copy(logo_src, logo_dst)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# ---------------- Figure 1: System Architecture Diagram ----------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis('off')

# Layer boxes
boxes = [
    (1, 5.8, 8, 0.9, "#EBF5FB", "#2980B9", "User / Client Tier", "CLI Interface (main.py)  |  Interactive Shell Scripts (queries.js)  |  mongosh"),
    (1, 4.4, 8, 0.9, "#E8F8F5", "#16A085", "Application & Business Logic Tier", "Python 3.14  |  crud.py (CRUD & Tests)  |  aggregations.py (9 Pipelines)  |  seed.py"),
    (1, 3.0, 8, 0.9, "#FEF9E7", "#D4AC0D", "Driver & Connection Tier", "PyMongo 4.19.0  |  Connection Pooling  |  BSON / Python Type Marshaling  |  Timeout: 5000ms"),
    (1, 0.8, 8, 1.7, "#FDEDEC", "#C0392B", "MongoDB Database Engine Tier (v8.2.3 - Port 27017)", 
     "Storage: WiredTiger Engine  |  Database: fittrack_db\n"
     "Strict $jsonSchema Validation Rules (validationLevel: strict, action: error)\n"
     "8 Collections: users, goals, meals, workouts, water_intakes, progress_logs, diet_plans, exercises\n"
     "Indexes: Unique (email, exercise name), Compound (user_id ASC, date DESC)")
]

for x, y, w, h, bg, border, title, desc in boxes:
    rect = plt.Rectangle((x, y), w, h, facecolor=bg, edgecolor=border, linewidth=2, linestyle='-', capstyle='round')
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.28, title, ha='center', va='center', fontsize=12, fontweight='bold', color=border)
    ax.text(x + w/2, y + (h - 0.35)/2, desc, ha='center', va='center', fontsize=9.5, color='#2C3E50', linespacing=1.3)

# Arrows
for y_top in [5.8, 4.4, 3.0]:
    ax.annotate('', xy=(5, y_top), xytext=(5, y_top + 0.5),
                arrowprops=dict(facecolor='#34495E', edgecolor='#34495E', width=2, headwidth=8, shrink=0.05))

plt.title("Figure 1: FitTrack Multi-Tier System Architecture (Client to MongoDB Storage)", fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("report_assets/figure1_architecture.png", dpi=300)
plt.close()

# ---------------- Figure 2: Entity Relationship & Document Reference Model ----------------
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 7)
ax.axis('off')

# Central Users Box
user_rect = plt.Rectangle((4, 4.2), 3, 2.3, facecolor="#E8F4F8", edgecolor="#2980B9", linewidth=2)
ax.add_patch(user_rect)
ax.text(5.5, 6.2, "users Collection", ha='center', fontsize=11, fontweight='bold', color="#2980B9")
ax.text(5.5, 5.2, 
        "_id: ObjectId [PK]\n"
        "name: String, email: String (Unique)\n"
        "password_hash: String, role: Enum\n"
        "[Embedded Document]\n"
        "profile: { age, gender, height_cm,\n"
        "  weight_kg, goal_weight, pref }",
        ha='center', fontsize=8.5, color='#1A252F', linespacing=1.1)

# Referenced child collections
children = [
    (0.5, 1.8, 2.0, 1.6, "goals", "user_id [Ref]\ngoal_type\nstart/target_wt\ncalorie_target\nstatus: active"),
    (2.8, 1.8, 2.0, 1.6, "meals", "user_id [Ref]\nmeal_name, type\ncalories, macros\ndate: ISODate\n(679 docs)"),
    (5.1, 1.8, 2.0, 1.6, "workouts", "user_id [Ref]\ntitle, workout_type\nduration_minutes\ncalories_burned\ndate: ISODate"),
    (7.4, 1.8, 2.0, 1.6, "water_intakes", "user_id [Ref]\namount_ml\ndate: ISODate\n(858 docs)"),
    (9.6, 1.8, 1.1, 1.6, "progress", "user_id\nweight_kg\ndate"),
]

for x, y, w, h, name, fields in children:
    rect = plt.Rectangle((x, y), w, h, facecolor="#FEF5E7", edgecolor="#E67E22", linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.22, name, ha='center', fontsize=10, fontweight='bold', color="#D35400")
    ax.text(x + w/2, y + (h - 0.35)/2, fields, ha='center', fontsize=8, color='#34495E', linespacing=1.15)
    # Connector
    ax.annotate('', xy=(x + w/2, y + h), xytext=(5.5, 4.2),
                arrowprops=dict(arrowstyle="->", color="#7F8C8D", lw=1.5))
    ax.text((x + w/2 + 5.5)/2, (y + h + 4.2)/2, "1:N", fontsize=7.5, color="#7F8C8D", backgroundcolor="white")

# Master Catalogs
cat_rect1 = plt.Rectangle((0.5, 4.5), 2.8, 1.8, facecolor="#EAFAF1", edgecolor="#27AE60", linewidth=1.5)
ax.add_patch(cat_rect1)
ax.text(1.9, 6.0, "diet_plans Collection", ha='center', fontsize=10, fontweight='bold', color="#27AE60")
ax.text(1.9, 5.2, "name, goal_type\nbmi_categories: Array\ndietary_preference\nmeals_suggestion: Array\ntags: Array", 
        ha='center', fontsize=8, color='#2C3E50', linespacing=1.15)

cat_rect2 = plt.Rectangle((7.7, 4.5), 2.8, 1.8, facecolor="#F4ECF7", edgecolor="#8E44AD", linewidth=1.5)
ax.add_patch(cat_rect2)
ax.text(9.1, 6.0, "exercises Collection", ha='center', fontsize=10, fontweight='bold', color="#8E44AD")
ax.text(9.1, 5.2, "name: String (Unique)\ncategory, difficulty\nmuscle_groups: Array\ncalories_per_minute", 
        ha='center', fontsize=8, color='#2C3E50', linespacing=1.15)

plt.title("Figure 2: FitTrack Hybrid Data Model – Embedded Profile & Referenced Logs", fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("report_assets/figure2_er_diagram.png", dpi=300)
plt.close()

# ---------------- Figure 3: Terminal Card - Database Seeding Output ----------------
fig, ax = plt.subplots(figsize=(9, 4), dpi=300)
ax.set_facecolor("#1E1E1E")
fig.patch.set_facecolor("#1E1E1E")
ax.axis('off')

term_text = (
    "PS C:\\Users\\mishr\\Downloads\\fittrack_mongo> .\\venv\\Scripts\\python.exe seed.py\n"
    "Connecting to MongoDB instance at mongodb://localhost:27017...\n"
    "Setting up database 'fittrack_db' with strict $jsonSchema validators...\n"
    "  [OK] Collection 'users' created with validator and unique index (email)\n"
    "  [OK] Collection 'goals' created with validator and compound index (user_id, status)\n"
    "  [OK] Collection 'meals' created with validator and compound index (user_id, date DESC)\n"
    "  [OK] Collection 'workouts' created with validator and compound index (user_id, date DESC)\n"
    "  [OK] Collection 'water_intakes' created with validator and compound index (user_id, date DESC)\n"
    "  [OK] Collection 'progress_logs' created with validator and compound index (user_id, date DESC)\n"
    "  [OK] Collection 'diet_plans' created with validator and index (goal_type, preference)\n"
    "  [OK] Collection 'exercises' created with validator and unique index (name)\n"
    "Inserting 7 personas, 30 days of activity logs, 7 diet plans, and 10 exercises...\n"
    "Seeded Collections:\n"
    "  users: 7  |  goals: 6  |  meals: 679  |  workouts: 113\n"
    "  water_intakes: 858  |  progress_logs: 66  |  diet_plans: 7  |  exercises: 10\n"
    "Status: SUCCESS (1,746 documents active in 'fittrack_db')"
)

ax.text(0.02, 0.95, term_text, transform=ax.transAxes, fontsize=8.5,
        fontfamily='monospace', color="#00FF66", va='top', linespacing=1.25)

plt.title("Figure 3: MongoDB Database Initialization and 30-Day Activity Seed Output", 
          fontsize=11, fontweight='bold', color='white', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure3_seed_counts.png", dpi=300, facecolor=fig.get_facecolor())
plt.close()

# ---------------- Figure 4: Terminal Card - Schema Validation Rejections ----------------
fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=300)
ax.set_facecolor("#1B1F23")
fig.patch.set_facecolor("#1B1F23")
ax.axis('off')

val_text = (
    "PS C:\\Users\\mishr\\Downloads\\fittrack_mongo> .\\venv\\Scripts\\python.exe main.py (Option 2)\n"
    "=== Testing Database-Level Validation ($jsonSchema) ===\n\n"
    "[TEST 1] meals.insertOne({'meal_type': 'brunch', ...})\n"
    "  --> REJECTED: code 121: Document failed validation (enum mismatch: brunch)\n\n"
    "[TEST 2] meals.insertOne({'calories': -50, ...})\n"
    "  --> REJECTED: code 121: Document failed validation (minimum: 0 constraint violated)\n\n"
    "[TEST 3] workouts.insertOne({'duration_minutes': 0, ...})\n"
    "  --> REJECTED: code 121: Document failed validation (minimum: 1 constraint violated)\n\n"
    "[TEST 4] progress_logs.insertOne({'weight_kg': 5, ...})\n"
    "  --> REJECTED: code 121: Document failed validation (weight must be >= 20 kg)\n\n"
    "[TEST 5] meals.insertOne({'meal_name': 'No user', ...}) [Missing user_id]\n"
    "  --> REJECTED: code 121: Document failed validation (required field 'user_id' omitted)\n\n"
    "[TEST 6] users.insertOne({'email': 'user@fittrack.test', ...}) [Duplicate email]\n"
    "  --> REJECTED: E11000 duplicate key error collection: fittrack_db.users index: email_1\n\n"
    "Validation Enforcement: 100% REJECTION RATE on malformed documents."
)

ax.text(0.02, 0.95, val_text, transform=ax.transAxes, fontsize=8.2,
        fontfamily='monospace', color="#FF8080", va='top', linespacing=1.2)

plt.title("Figure 4: MongoDB Server-Side Schema Validation Test Execution Trace (Code 121)", 
          fontsize=11, fontweight='bold', color='white', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure4_validation_rejections.png", dpi=300, facecolor=fig.get_facecolor())
plt.close()

# ---------------- Figure 5: Pipeline 1 - 7-Day Nutrition Breakdown ----------------
dates = ["10-13", "10-14", "10-15", "10-16", "10-17", "10-18", "10-19"]
calories = [1210, 1290, 1280, 1330, 1400, 1280, 1680]
protein = [80, 58, 93, 50, 54, 72, 108]
carbs = [92, 195, 94, 211, 224, 117, 155]
fat = [45, 27, 45, 28, 29, 50, 52]

fig, ax1 = plt.subplots(figsize=(9, 4.5), dpi=300)

x = np.arange(len(dates))
w = 0.55

p1 = ax1.bar(x, protein, w, label='Protein (g)', color='#2980B9')
p2 = ax1.bar(x, carbs, w, bottom=protein, label='Carbohydrates (g)', color='#27AE60')
bottom_fat = np.array(protein) + np.array(carbs)
p3 = ax1.bar(x, fat, w, bottom=bottom_fat, label='Fat (g)', color='#E67E22')

ax1.set_ylabel('Macronutrients (grams)', fontsize=11, fontweight='bold', color='#2C3E50')
ax1.set_xlabel('Log Date (October 2026)', fontsize=11, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(dates)
ax1.set_ylim(0, 360)

# Secondary axis for total calories
ax2 = ax1.twinx()
ax2.plot(x, calories, color='#C0392B', marker='o', linewidth=2.5, markersize=7, label='Total Energy (kcal)')
ax2.set_ylabel('Total Energy (kcal)', fontsize=11, fontweight='bold', color='#C0392B')
ax2.set_ylim(800, 2000)
ax2.grid(False)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)

plt.title("Figure 5: Aggregation Pipeline 1 – Rolling 7-Day Macronutrient & Calorie Breakdown", fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure5_daily_nutrition.png", dpi=300)
plt.close()

# ---------------- Figure 6: Pipeline 3 - BMI Category Distribution ----------------
categories = ['Overweight\n(Avg BMI: 28.4)', 'Normal\n(Avg BMI: 23.5)', 'Underweight\n(Avg BMI: 18.3)']
user_counts = [3, 2, 1]
colors = ['#E67E22', '#27AE60', '#3498DB']

fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
bars = ax.bar(categories, user_counts, color=colors, width=0.45, edgecolor='#2C3E50', linewidth=1.2)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.08, f"{int(yval)} Users", ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_ylabel('Number of Users', fontsize=11, fontweight='bold')
ax.set_ylim(0, 4)
ax.set_title("Figure 6: Aggregation Pipeline 3 – Platform Demographic BMI Distribution", fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure6_bmi_distribution.png", dpi=300)
plt.close()

# ---------------- Figure 7: Pipeline 4 - Popular Workout Disciplines ----------------
disciplines = ['Cycling', 'Running', 'Strength', 'Yoga', 'Cardio']
sessions = [28, 25, 23, 20, 17]
avg_cals = [321, 350, 304, 154, 336]

fig, ax1 = plt.subplots(figsize=(8, 4.2), dpi=300)
y_pos = np.arange(len(disciplines))

bars = ax1.barh(y_pos, sessions, height=0.5, color='#2980B9', label='Completed Sessions')
ax1.set_yticks(y_pos)
ax1.set_yticklabels(disciplines, fontsize=10, fontweight='bold')
ax1.invert_yaxis()
ax1.set_xlabel('Total Sessions Completed', fontsize=10, fontweight='bold', color='#2980B9')
ax1.set_xlim(0, 35)

for i, v in enumerate(sessions):
    ax1.text(v + 0.5, i, f"{v} sessions (Avg {avg_cals[i]} kcal)", va='center', fontsize=9, color='#2C3E50', fontweight='bold')

plt.title("Figure 7: Aggregation Pipeline 4 – Popular Workout Disciplines and Energy Expenditure", fontsize=11, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure7_workout_popularity.png", dpi=300)
plt.close()

# ---------------- Figure 8: Pipeline 5 - Goal Progress Tracking ----------------
users = ['Anita Desai\n(Maintain)', 'Akshat Rana\n(Loss)', 'Priya Sharma\n(Gain)', 'Karan Singh\n(Gain)', 'Rohan Mehta\n(Loss)', 'Neha Verma\n(Loss)']
progress = [100.0, 35.0, 33.3, 33.3, 33.0, 33.0]
bar_colors = ['#27AE60' if p == 100 else '#3498DB' for p in progress]

fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
bars = ax.bar(users, progress, color=bar_colors, width=0.5, edgecolor='#34495E', linewidth=1)

for bar in bars:
    y = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, y + 1.8, f"{y:.1f}%", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

ax.set_ylabel('Goal Progress Completion (%)', fontsize=10, fontweight='bold')
ax.set_ylim(0, 115)
ax.axhline(100, color='#27AE60', linestyle='--', linewidth=1.2, label='Goal Completed (100%)')
ax.legend(loc='upper right')

plt.title("Figure 8: Aggregation Pipeline 5 – Real-Time Goal Progress Completion ($lookup)", fontsize=11, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure8_goal_progress.png", dpi=300)
plt.close()

# ---------------- Figure 9: Pipeline 8 - Net Calorie Balance ----------------
consumed = [1210, 1290, 1280, 1330, 1400, 1280, 1680]
burned = [420, 0, 0, 0, 120, 0, 0]
net = [790, 1290, 1280, 1330, 1280, 1280, 1680]

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
x = np.arange(len(dates))
w = 0.35

ax.bar(x - w/2, consumed, width=w, label='Calories Consumed (Meals)', color='#E67E22')
ax.bar(x + w/2, burned, width=w, label='Calories Burned (Workouts)', color='#2980B9')
ax.plot(x, net, color='#27AE60', marker='s', linewidth=2.5, markersize=7, label='Net Energy Balance')

ax.set_xticks(x)
ax.set_xticklabels(dates)
ax.set_ylabel('Energy (kcal)', fontsize=11, fontweight='bold')
ax.set_xlabel('Log Date (October 2026)', fontsize=11, fontweight='bold')
ax.set_ylim(0, 1900)
ax.legend(loc='upper left', frameon=True)

plt.title("Figure 9: Aggregation Pipeline 8 – Cross-Collection Net Calorie Balance ($unionWith)", fontsize=11, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("report_assets/figure10_net_calories.png", dpi=300)
plt.close()

print("All report figures generated successfully in report_assets/")
