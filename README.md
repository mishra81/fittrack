# FitTrack: Health and Diet Tracker

FitTrack is a full-stack Health and Diet Tracker built with Laravel 12, PHP 8, SQLite/MySQL, Blade, Tailwind CSS, Laravel Breeze authentication, Eloquent ORM, RESTful controllers, Laravel Sanctum APIs, and Chart.js analytics.

The goal of this project is to help users track their health and fitness journey from one dashboard. Users can manage meals, calories, macros, workouts, weight goals, BMI, water intake, and diet recommendations. Admin users can manage users, diet plans, exercises, and view platform-level statistics.

## Project Objective

Many people struggle to maintain fitness goals because their meal logs, workouts, body metrics, and progress are scattered across different tools. This project solves that problem by providing a centralized web application where users can:

- Track daily meals and calories.
- Track protein, carbs, and fat intake.
- Track workouts and calories burned.
- Monitor BMI and weight changes.
- Set weight loss, weight gain, or maintenance goals.
- View dashboard analytics.
- Get diet recommendations based on BMI, goal type, activity level, and dietary preference.
- Track daily water intake.
- Use an admin panel for managing users, diet plans, and exercise records.

## Technology Stack

- Laravel 12
- PHP 8.2+
- SQLite for local development, MySQL-ready through `.env`
- Blade templates
- Tailwind CSS
- Laravel Breeze authentication
- Laravel Sanctum API authentication
- Eloquent ORM
- Chart.js
- Vite
- PHPUnit

## Main Features

### Authentication

Authentication is handled using Laravel Breeze.

Features:

- Register
- Login
- Logout
- Forgot password
- Reset password
- Email verification
- Password update
- Account deletion

Important files:

- `routes/auth.php`
- `app/Http/Controllers/Auth/*`
- `resources/views/auth/*`

### Dashboard

The user dashboard shows a complete health summary:

- Current weight
- Goal weight
- Daily calories consumed
- Calories burned
- Water intake progress
- BMI and BMI category
- Workout streak
- Weekly calorie analytics
- Weight trend
- Workout consistency
- Meal calorie split
- Recommended diet plans

Important files:

- `app/Http/Controllers/DashboardController.php`
- `app/Services/AnalyticsService.php`
- `resources/views/dashboard.blade.php`

### Profile Module

The profile stores user health information:

- Age
- Gender
- Height
- Weight
- Goal weight
- Activity level
- Dietary preference
- Profile photo

BMI is calculated automatically using:

```text
BMI = weight(kg) / height(m)^2
```

BMI category:

- Underweight: below 18.5
- Normal: 18.5 to 24.9
- Overweight: 25 to 29.9
- Obese: 30 and above

Important files:

- `app/Models/Profile.php`
- `app/Services/HealthMetricService.php`
- `app/Http/Controllers/ProfileController.php`
- `resources/views/profile/edit.blade.php`

### Meal Tracking

Users can log:

- Meal name
- Calories
- Protein
- Carbs
- Fat
- Meal type: breakfast, lunch, dinner, snack
- Date

The dashboard automatically sums calories for today's date.

Important files:

- `app/Models/Meal.php`
- `app/Http/Controllers/MealController.php`
- `app/Http/Requests/MealRequest.php`
- `resources/views/meals/*`

### Workout Tracking

Users can log:

- Workout title
- Workout type
- Duration in minutes
- Calories burned
- Date

Supported workout types:

- Cardio
- Strength
- Yoga
- Running
- Cycling

Important files:

- `app/Models/Workout.php`
- `app/Http/Controllers/WorkoutController.php`
- `app/Http/Requests/WorkoutRequest.php`
- `resources/views/workouts/*`

### Goal Management

Users can create goals for:

- Weight loss
- Weight gain
- Maintenance

Goal fields:

- Start weight
- Target weight
- Daily calorie target
- Workout frequency target
- Start date
- Target date
- Status

The application calculates goal progress as a percentage.

Important files:

- `app/Models/Goal.php`
- `app/Http/Controllers/GoalController.php`
- `app/Http/Requests/GoalRequest.php`
- `resources/views/goals/*`

### Water Intake Tracker

Users can log water intake in milliliters.

Default goal:

```text
3000 ml per day
```

Important files:

- `app/Models/WaterIntake.php`
- `app/Http/Controllers/WaterIntakeController.php`
- `app/Http/Requests/WaterIntakeRequest.php`
- `resources/views/water-intakes/index.blade.php`

### Diet Recommendation Engine

The recommendation system suggests diet plans based on:

- BMI
- Active goal
- Activity level
- Dietary preference

Example plans:

- Weight Loss Diet
- Muscle Gain Diet
- Vegan Plan
- High Protein Plan

Important files:

- `app/Models/DietPlan.php`
- `app/Services/DietRecommendationService.php`
- `app/Http/Controllers/DietRecommendationController.php`
- `resources/views/recommendations/index.blade.php`

### Admin Panel

Admin users can:

- View total users
- View active users
- View average calories tracked
- View most used workout types
- Manage users
- Manage diet plans
- Manage exercise library

Important files:

- `app/Http/Controllers/Admin/DashboardController.php`
- `app/Http/Controllers/Admin/UserController.php`
- `app/Http/Controllers/Admin/DietPlanController.php`
- `app/Http/Controllers/Admin/ExerciseController.php`
- `resources/views/admin/*`

## Database Tables

The project includes migrations for:

- `users`
- `profiles`
- `meals`
- `workouts`
- `goals`
- `water_intakes`
- `diet_plans`
- `progress_logs`
- `exercises`
- `notifications`
- `personal_access_tokens`
- Laravel system tables: sessions, jobs, cache, password reset tokens

Main relationships:

- User has one Profile
- User has many Meals
- User has many Workouts
- User has many Goals
- User has many WaterIntakes
- User has many ProgressLogs
- DietPlan is managed by admin
- Exercise is managed by admin

Important files:

- `database/migrations/*`
- `database/seeders/DatabaseSeeder.php`

## PyMongo Health-Data Service

The optional PyMongo service stores profiles, meals, workouts, goals, water intakes, progress logs, diet plans, and exercises in MongoDB. User-owned documents link to the authenticated Laravel account through its integer `user_id`; authentication and Laravel's existing Eloquent-backed pages remain on SQL.

The Sanctum-protected `/api/health-data/{collection}` endpoints forward requests to the Python service. The service validates each collection's document schema, creates indexes on startup, scopes user records to the authenticated Laravel user, and restricts writes to diet plans and exercises to administrators.

Set up the Python service from the repository root in PowerShell:

```powershell
python -m pip install -r mongo_service\requirements.txt
Copy-Item mongo_service\.env.example mongo_service\.env
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Put the generated token in `mongo_service\.env` as `FITTRACK_SERVICE_TOKEN` and in Laravel's `.env` as `PYMONGO_SERVICE_TOKEN`. Configure `MONGODB_URI` and `MONGODB_DATABASE` in the service environment, then start MongoDB and run:

```powershell
python -m mongo_service
```

The service listens on `127.0.0.1:8001` by default. Configure `PYMONGO_SERVICE_URL` in Laravel's `.env` if it is running elsewhere. The existing Blade screens and `/api/meals`, `/api/workouts`, and `/api/goals` endpoints are not migrated and continue to use SQL.

## Code Architecture

This project follows Laravel MVC architecture.

### Models

Models represent database tables and relationships.

Location:

```text
app/Models
```

Examples:

- `User.php`
- `Profile.php`
- `Meal.php`
- `Workout.php`
- `Goal.php`
- `DietPlan.php`

### Controllers

Controllers receive requests, call models/services, and return views or JSON responses.

Location:

```text
app/Http/Controllers
```

Examples:

- `DashboardController.php`
- `MealController.php`
- `WorkoutController.php`
- `GoalController.php`
- `WaterIntakeController.php`

### Form Requests

Form request classes handle validation.

Location:

```text
app/Http/Requests
```

Examples:

- `MealRequest.php`
- `WorkoutRequest.php`
- `GoalRequest.php`
- `ProfileUpdateRequest.php`

Validation examples:

- Calories must be numeric.
- Weight must be positive.
- Password must be confirmed.
- Email must be unique.
- Workout duration must be at least 1 minute.

### Services

Services keep business logic separate from controllers.

Location:

```text
app/Services
```

Services:

- `HealthMetricService`: calculates BMI and BMI category.
- `AnalyticsService`: prepares chart data for the dashboard.
- `DietRecommendationService`: recommends diet plans.

### Views

Blade views handle the frontend UI.

Location:

```text
resources/views
```

Main view folders:

- `auth`
- `profile`
- `meals`
- `workouts`
- `goals`
- `water-intakes`
- `recommendations`
- `admin`

### Routes

Web routes:

```text
routes/web.php
```

API routes:

```text
routes/api.php
```

Authentication routes:

```text
routes/auth.php
```

## REST API

The project includes Sanctum-based API authentication.

Public endpoints:

```text
POST /api/register
POST /api/login
```

Authenticated endpoints:

```text
POST /api/logout
GET /api/user
GET /api/analytics
```

Meal API:

```text
GET /api/meals
POST /api/meals
GET /api/meals/{meal}
PUT /api/meals/{meal}
DELETE /api/meals/{meal}
```

Workout API:

```text
GET /api/workouts
POST /api/workouts
GET /api/workouts/{workout}
PUT /api/workouts/{workout}
DELETE /api/workouts/{workout}
```

Goal API:

```text
GET /api/goals
POST /api/goals
GET /api/goals/{goal}
PUT /api/goals/{goal}
DELETE /api/goals/{goal}
```

Use this header for authenticated API requests:

```text
Authorization: Bearer YOUR_TOKEN
```

## Security Features

- Laravel Breeze authentication
- Secure password hashing
- CSRF protection for web forms
- Sanctum token authentication for APIs
- Email verification
- Middleware-protected routes
- Admin routes protected with `access-admin` gate
- Validation through Form Request classes
- Blade escaping to reduce XSS risk
- User-owned records protected through ownership checks and policies

## Local Setup

Open the project folder in VS Code:

```powershell
cd "C:\Users\Akshat Rana\Documents\New project\health-diet-tracker"
```

Install PHP dependencies:

```powershell
composer install
```

Install Node dependencies:

```powershell
npm install
```

Create environment file:

```powershell
copy .env.example .env
```

Generate app key:

```powershell
php artisan key:generate
```

Create storage link:

```powershell
php artisan storage:link
```

Run migrations and seed sample data:

```powershell
php artisan migrate:fresh --seed
```

Build frontend assets:

```powershell
npm.cmd run build
```

## Running the Project

Open one VS Code terminal and run:

```powershell
php artisan serve --host=127.0.0.1 --port=8000
```

Open a second VS Code terminal and run:

```powershell
npm.cmd run dev
```

Open the application:

```text
http://127.0.0.1:8000
```

Important:

- `http://127.0.0.1:8000` is the Laravel application.
- `http://localhost:5173` is only the Vite asset server.

## Demo Login Credentials

User account:

```text
Email: user@fittrack.test
Password: password
```

Admin account:

```text
Email: admin@fittrack.test
Password: password
```

## Presentation Flow

Use this flow when presenting to a teacher or class:

1. Open the landing page and explain the project objective.
2. Login as the user account.
3. Show the dashboard cards: calories, weight, BMI, burned calories, water, and workout streak.
4. Show Chart.js analytics.
5. Add a meal and explain calorie and macro tracking.
6. Add a workout and explain burned calorie tracking.
7. Open goals and explain goal progress.
8. Open water tracker and explain the hydration progress bar.
9. Open diet recommendations and explain the recommendation logic.
10. Logout and login as admin.
11. Show admin dashboard, user management, diet plan management, and exercise management.
12. Explain that the backend also includes REST APIs through Sanctum.

## Code Explanation for Presentation

You can explain the code like this:

1. Laravel Breeze handles login, registration, password reset, and email verification.
2. Routes are defined in `routes/web.php` for web pages and `routes/api.php` for REST APIs.
3. Controllers handle user actions, such as adding meals or workouts.
4. Form Request classes validate all form input before saving to the database.
5. Eloquent models represent tables and define relationships.
6. Services contain reusable business logic like BMI calculation, analytics data, and diet recommendations.
7. Blade views and Tailwind CSS create the user interface.
8. Chart.js displays progress analytics on the dashboard.
9. Admin routes are protected using middleware and the `access-admin` gate.
10. Seeders create demo users, meals, workouts, goals, diet plans, and exercises.

## Testing

Run all tests:

```powershell
php artisan test
```

The test suite checks:

- Authentication
- Registration
- Password reset
- Profile update
- Meal tracking
- Dashboard calorie update

## Deployment Notes

This project should be deployed on a platform that supports PHP and databases.

Recommended hosting options:

- Railway
- Render
- DigitalOcean
- Laravel Forge
- Shared PHP hosting with MySQL

Vercel is not ideal for this project because Vercel is mainly designed for frontend and serverless JavaScript applications. This app is a full Laravel PHP application that needs a PHP runtime, database, storage, migrations, and environment configuration.

## Future Enhancements

Possible improvements:

- PDF health reports
- Dark mode toggle
- AI calorie estimator
- Food barcode or QR scanner
- Fitness streak badges
- PWA support
- Wearable device integration
- Community challenges
- Notification scheduler for meals, workouts, and water reminders

## Conclusion

FitTrack is a complete Laravel-based health tracking platform. It combines authentication, user profiles, meal tracking, workout tracking, BMI calculation, goal management, diet recommendations, water tracking, analytics, REST APIs, and an admin panel into one full-stack project.
