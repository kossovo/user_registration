import re

email_regex = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)


def is_valid_email(email):
    if email and re.fullmatch(pattern=email_regex, string=email):
        return True
    return False
