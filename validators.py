import re
# FULL NAME
def validate_full_name(name):
    name = name.strip()
    if len(name.split()) < 2:
        return False
    pattern = r"^[A-Za-z]+(?:\s[A-Za-z]+)+$"
    return bool(re.match(pattern, name))
# EMAIL
def validate_email(email):
    email = email.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[gmail]+\.[com]{2,}$"
    return bool(re.match(pattern, email))
# PHONE (10 DIGITS ONLY)
def validate_phone(phone):
    digits = re.sub(r"\D", "", phone)
    return len(digits) == 10
# EXPERIENCE (4.5 allowed)
def validate_experience(exp):
    exp = exp.strip()
    pattern = r"^\d+(\.\d+)?$"
    if not re.match(pattern, exp):
        return False
    years = float(exp)
    if 0 <= years <= 50:
        return True
    return False
# TECH STACK
def validate_tech_stack(stack):
    stack = stack.strip()
    if len(stack) < 3:
        return False
    items = [x.strip() for x in stack.split(",") if x.strip()]
    if len(items) == 0:
        return False
    for item in items:
        if not re.search(r"[A-Za-z]", item):
            return False
        if len(item) < 2:
            return False
    return True
# EXIT COMMAND
def is_exit_command(text):
    exit_words = ["exit", "quit", "bye", "stop"]
    return any(word in text.lower() for word in exit_words)