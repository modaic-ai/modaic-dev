# schemas/user.py
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import Optional, List
from src.utils.date import now
import re


class UserSchema(BaseModel):
    """Full user schema with all fields - for internal use and owner access."""

    userId: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # sensitive - not in public schema
    created: str
    updated: str
    fullName: Optional[str] = Field(None, max_length=255)
    profilePictureUrl: Optional[str] = Field(None, max_length=500)

    #new fields
    bio: Optional[str] = Field(None, max_length=1000)
    githubUrl: Optional[str] = Field(None, max_length=500)
    linkedinUrl: Optional[str] = Field(None, max_length=500)
    xUrl: Optional[str] = Field(None, max_length=500)
    websiteUrl: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class PublicUserSchema(BaseModel):
    """Public user schema - what others can see."""

    userId: str
    username: str
    fullName: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    created: str

    #new fields
    bio: Optional[str] = None
    githubUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None
    xUrl: Optional[str] = None
    websiteUrl: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreateUserRequest(BaseModel):
    """Request schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    fullName: Optional[str] = Field(None, max_length=255)
    profilePictureUrl: Optional[str] = Field(None, max_length=500)

    #new fields
    bio: Optional[str] = Field(None, max_length=1000)
    githubUrl: Optional[str] = Field(None, max_length=500)
    linkedinUrl: Optional[str] = Field(None, max_length=500)
    xUrl: Optional[str] = Field(None, max_length=500)
    websiteUrl: Optional[str] = Field(None, max_length=500)

    # auto-generated fields
    created: str = Field(default_factory=lambda: now())
    updated: str = Field(default_factory=lambda: now())

    @validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, hyphens, and underscores"
            )
        return v.lower()

    @validator("profilePictureUrl")
    def validate_profile_picture_url(cls, v):
        """Validate profile picture URL format."""
        if v and not re.match(r"^https?://", v):
            raise ValueError("Profile picture URL must start with http:// or https://")
        return v


class UpdateUserRequest(BaseModel):
    """Request schema for updating user information."""

    fullName: Optional[str] = Field(None, max_length=255)
    profilePictureUrl: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    githubUrl: Optional[str] = Field(None, max_length=500)
    linkedinUrl: Optional[str] = Field(None, max_length=500)
    xUrl: Optional[str] = Field(None, max_length=500)
    websiteUrl: Optional[str] = Field(None, max_length=500)

    # auto-updated field
    updated: str = Field(default_factory=lambda: now())

    @validator("profilePictureUrl")
    def validate_profile_picture_url(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError("Profile picture URL must start with http:// or https://")
        return v
    
    @validator("xUrl")
    def validate_x_url(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError("X URL must start with http:// or https://")
        return v

    @validator("githubUrl")
    def validate_github_url(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError("GitHub URL must start with http:// or https://")
        return v

    @validator("websiteUrl")
    def validate_website_url(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError("Website URL must start with http:// or https://")
        return v

    @validator("linkedinUrl")
    def validate_linkedin_url(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError("LinkedIn URL must start with http:// or https://")
        return v

    model_config = ConfigDict(exclude_unset=True)


class DeleteUserRequest(BaseModel):
    """Request schema for deleting a user."""

    userId: str = Field(..., min_length=1, max_length=100)
    # Could add confirmation field if needed
    confirm_deletion: bool = Field(default=False)


class UserSearchRequest(BaseModel):
    """Request schema for searching users."""

    query: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Search in username or fullName"
    )
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class UserListResponse(BaseModel):
    """Response schema for user list endpoints."""

    users: List[PublicUserSchema]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1)
    total_pages: int = Field(..., ge=0)

    @validator("total_pages", pre=True, always=True)
    def calculate_total_pages(cls, v, values):
        total = values.get("total", 0)
        size = values.get("size", 20)
        return (total + size - 1) // size if total > 0 else 0


class UserResponse(BaseModel):
    """Standard response wrapper for user operations."""

    success: bool
    data: Optional[UserSchema] = None
    message: Optional[str] = None

# validation helpers
class UserValidation:
    """Helper class for user validation logic."""

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Check if username format is valid."""
        return bool(re.match(r"^[a-zA-Z0-9_-]{3,50}$", username))

    @staticmethod
    def is_valid_profile_url(url: str) -> bool:
        """Check if profile picture URL is valid."""
        return bool(re.match(r"^https?://.+\.(jpg|jpeg|png|gif|webp)$", url, re.I))

    @staticmethod
    def sanitize_username(username: str) -> str:
        """Sanitize username input."""
        return re.sub(r"[^a-zA-Z0-9_-]", "", username).lower()[:50]
