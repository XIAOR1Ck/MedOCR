import re


class EmailValidator:
    # Regex pattern for basic email validation
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    @staticmethod
    def validate(email: str):
        is_valid = False
        if isinstance(email, str):
            is_valid = re.match(EmailValidator.EMAIL_REGEX, email) is not None
        return {"email": email, "is_valid": is_valid}

    @staticmethod
    def get_error_message():
        return "Invalid email address format."
