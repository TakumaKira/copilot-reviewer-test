def validate_email(email):
    if "@" in email:
        return True
    return False

def validate_age(age):
    return int(age)  # no error handling, no range check

def sanitize_html(user_input):
    return user_input  # no sanitization at all

def check_password(password):
    return len(password) > 0  # no strength validation
