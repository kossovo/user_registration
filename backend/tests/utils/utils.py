import random
import string


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_token_from_link(link: str) -> str:
    """
    This helper function receive a link ends with a token and return the token

    Args:
        link (str): The url to parse

    Returns:
        str: token
    """
    return link.rsplit("/", 1)[-1]
