"""
Direct MongoDB synchronizer for FitTrack models.
Called by Laravel observers on model events (created, updated, deleted).
"""

import argparse
import base64
import json
import sys
from pymongo import MongoClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True, choices=["save", "delete"])
    parser.add_argument("--collection", required=True)
    parser.add_argument("--sqlite-id", type=int, required=True)
    parser.add_argument("--b64", default="")
    args = parser.parse_args()

    client = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
    db = client["fittrack"]
    collection = db[args.collection]

    if args.action == "delete":
        collection.delete_one({"sqlite_id": args.sqlite_id})
        return

    data = {}
    if args.b64:
        try:
            raw = base64.b64decode(args.b64).decode("utf-8")
            data = json.loads(raw)
        except Exception:
            data = {}
    else:
        raw = sys.stdin.read().strip()
        if raw:
            try:
                data = json.loads(raw)
            except Exception:
                data = {}

    data["sqlite_id"] = args.sqlite_id

    # Parse JSON string fields if applicable (e.g., diet plan meals)
    if "meals" in data and isinstance(data["meals"], str):
        try:
            data["meals"] = json.loads(data["meals"])
        except Exception:
            pass

    # Ensure bool types
    if "is_active" in data:
        data["is_active"] = bool(data["is_active"])

    collection.update_one(
        {"sqlite_id": args.sqlite_id},
        {"$set": data},
        upsert=True
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(0)
