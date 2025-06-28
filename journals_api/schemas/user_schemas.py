
from datetime import date
from typing import Optional

from ninja import Schema
from pydantic import EmailStr, field_validator

class DjangoUserSchema(Schema):
    """
    Schema for Django User model.
    """
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    date_joined: date
    last_login: Optional[date]


# === Input Schemas ===
class RegisterSchema(Schema):
    """
    Schema for user registration.
    """
    username: str
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password security requirements."""
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValueError("Password must contain at least one special character")
        
        return password

class LoginSchema(Schema):
    """
    Schema for user login.
    """
    username: str # Can be username or email
    password: str

class PinSchema(Schema):
    """
    Schema for PIN input.
    """
    pin: str

class PasswordResetRequestSchema(Schema):
    """
    Schema for password reset request.
    """
    email: str

class PasswordResetConfirmSchema(Schema):
    """
    Schema for password reset confirmation.
    """
    token: str
    new_password: str

# === Output Schemas ===
class UserProfileSchema(Schema):
    """
    Schema for user profile.
    """
    id: int
    current_streak: int
    longest_streak: int
    last_content_date: Optional[date]
    has_pin: bool # Derived property

class UserSchema(Schema):
    """
    Schema for user.
    """
    id: int
    username: str
    email: str
    profile: UserProfileSchema


class RefreshSchema(Schema):
    """
    Schema for token refresh.
    """
    refresh: str