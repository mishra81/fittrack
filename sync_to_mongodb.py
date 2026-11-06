"""
Sync SQLite database to MongoDB for FitTrack
Usage: python sync_to_mongodb.py
"""

import json
import sqlite3
from pathlib import Path
from pymongo import MongoClient

SQLITE_PATH = Path(__file__).resolve().parent / "database" / "database.sqlite"
MONGO_URI = "mongodb://127.0.0.1:27017"
DB_NAME = "fittrack"

TABLES = [
    "users",
    "profiles",
    "meals",
    "workouts",
    "goals",
    "water_intakes",
    "diet_plans",
    "progress_logs",
    "exercises",
]

def sync():
    if not SQLITE_PATH.exists():
        print(f"Error: SQLite database not found at {SQLITE_PATH}")
        return

    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print(f"Connecting to MongoDB database '{DB_NAME}' at {MONGO_URI}...")
    
    total_docs = 0
    for table in TABLES:
        cur.execute(f"SELECT * FROM {table}")
        rows = [dict(r) for r in cur.fetchall()]

        processed_rows = []
        for r in rows:
            item = dict(r)
            if "meals" in item and isinstance(item["meals"], str):
                try:
                    item["meals"] = json.loads(item["meals"])
                except Exception:
                    pass
            if "is_active" in item:
                item["is_active"] = bool(item["is_active"])
            item["sqlite_id"] = item.get("id")
            processed_rows.append(item)

        collection = db[table]
        collection.delete_many({})
        if processed_rows:
            collection.insert_many(processed_rows)
            count = collection.count_documents({})
            print(f"  [+] {table}: synced {count} documents")
            total_docs += count
        else:
            print(f"  [-] {table}: 0 rows found in SQLite")

    print(f"\nCompleted! Total {total_docs} documents synced to MongoDB.")

if __name__ == "__main__":
    sync()
