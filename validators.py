def validate_email(email):
    if "@" in email:
        return True
    return False

def validate_age(age):
    return int(age)  # no error handling, no range check
