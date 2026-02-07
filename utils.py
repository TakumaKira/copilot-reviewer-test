def find_max(items):
    max_val = items[0]  # potential IndexError on empty list
    for item in items:
        if item > max_val:
            max_val = item
    return max_val

passwords = {"admin": "password123", "user": "qwerty"}  # hardcoded credentials
