import re
import uuid
from src.objects.index import User


def generate_username(email: str) -> str:
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

    # Basic email validation
    if "@" not in email:
        raise ValueError("Invalid email format")

    # Extract username part from email (before @)
    base_username = email.split("@")[0].lower()

    # Clean the username: remove non-alphanumeric characters except underscores
    base_username = re.sub(r"[^a-z0-9_]", "", base_username)

    # Ensure minimum length
    if len(base_username) < 3:
        base_username = f"{base_username}"

    # Check if base username is available
    if not Users.find_one({"username": base_username}):
        return base_username

    # If base username exists, try with incrementing numbers
    counter = 1
    while counter <= 999:
        candidate = f"{base_username}{counter}"
        if not Users.find_one({"username": candidate}):
            return candidate
        counter += 1

    # If all numbered variants are taken, use UUID suffix for guaranteed uniqueness
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{base_username}_{unique_suffix}"
