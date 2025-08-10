import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "premium_keys": {}, "banned": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_banned(user_id):
    data = load_data()
    return user_id in data.get("banned", [])

def ban_user(user_id):
    data = load_data()
    if user_id not in data.get("banned", []):
        data.setdefault("banned", []).append(user_id)
        save_data(data)

def unban_user(user_id):
    data = load_data()
    if user_id in data.get("banned", []):
        data["banned"].remove(user_id)
        save_data(data)

def add_premium_key(key, days):
    data = load_data()
    expire_date = (datetime.now() + timedelta(days=days)).timestamp()
    data.setdefault("premium_keys", {})[key] = expire_date
    save_data(data)

def check_key_valid(key):
    data = load_data()
    if key in data.get("premium_keys", {}):
        expire = datetime.fromtimestamp(data["premium_keys"][key])
        return expire > datetime.now()
    return False

def use_key(key):
    # You can add logic if you want to track key usage
    pass

def set_user_premium(user_id, key):
    data = load_data()
    expire = datetime.fromtimestamp(data["premium_keys"].get(key, 0))
    data.setdefault("users", {}).setdefault(str(user_id), {})["premium_expire"] = expire.timestamp()
    save_data(data)

def is_user_premium(user_id):
    data = load_data()
    user = data.get("users", {}).get(str(user_id), {})
    expire_timestamp = user.get("premium_expire", 0)
    if expire_timestamp:
        expire = datetime.fromtimestamp(expire_timestamp)
        return expire > datetime.now()
    return False

def mark_redeem_used(user_id):
    data = load_data()
    data.setdefault("users", {}).setdefault(str(user_id), {})["redeem_used"] = True
    save_data(data)

def has_used_redeem(user_id):
    data = load_data()
    return data.get("users", {}).get(str(user_id), {}).get("redeem_used", False)

def get_all_users():
    data = load_data()
    return list(data.get("users", {}).keys())
