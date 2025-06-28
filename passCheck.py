import re


def validate_password(password):
    # Check minimum length

    errors = []

    # Check minimum length
    if len(password) < 8:
        errors.append("be at least 8 characters long")

    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        errors.append("contain at least one uppercase letter")

    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        errors.append("contain at least one lowercase letter")

    # Check for at least one digit
    if not re.search(r"[0-9]", password):
        errors.append("contain at least one digit")

    # Check for at least one special character
    if not re.search(r"[!@#\$\-_%&]", password):
        errors.append("contain at least one special character (!@#$-_%&)")

    if errors:
        return False, "Password must: " + ", ".join(errors)
    else:
        return True, "Password is valid"
