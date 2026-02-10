import json

def load_cache(path):
    with open(path) as f:
        data = json.load(f)
    return data

def save_cache(path, data):
    with open(path, "w") as f:
        f.write(str(data))  # should use json.dump, not str()

def get_user_data(cache, user_id):
    return cache[user_id]  # KeyError if user_id not found
