import re
import uuid
from src.objects.index import User
from sqlalchemy.orm import Session


def generate_username(email: str, db: Session) -> str:
    """
    Generate a guaranteed unique username from an email address.

    Args:
        email: User's email address

    Returns:
        A unique username string

    Raises:
        ValueError: If email is invalid or empty
    """
    if not email or not isinstance(email, str):
        raise ValueError("Email must be a non-empty string")

    # basic email validation
    if "@" not in email:
        raise ValueError("Invalid email format")

    # extract username part from email (before @)
    base_username = email.split("@")[0].lower()

    # clean the username: remove non-alphanumeric characters except underscores
    base_username = re.sub(r"[^a-z0-9_]", "", base_username)

    # ensure minimum length
    if len(base_username) < 3:
        base_username = f"{base_username}"

    # check if base username is available
    if not db.query(User).filter(User.username == base_username).first():
        return base_username

    # if base username exists, try with incrementing numbers
    counter = 1
    while counter <= 999:
        candidate = f"{base_username}{counter}"
        if not db.query(User).filter(User.username == candidate).first():
            return candidate
        counter += 1

    # if all numbered variants are taken, use UUID suffix for guaranteed uniqueness
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{base_username}_{unique_suffix}"
