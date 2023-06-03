import json

def load_blocked_users():
    blocked_users = None
    try:
        with open('status/blocked_users.json', 'r') as f:
            blocked_users = json.load(f)
    except:
        blocked_users = {}
    return blocked_users

def save_blocked_users(blocked_users):
    with open('status/blocked_users.json', 'w') as f:
        json.dump(blocked_users, f)