from django.contrib.auth.models import User
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken

from ..models.user_model import UserProfile
from ..schemas.user_schemas import (LoginSchema,
                                    PinSchema, RefreshSchema, 
                                    RegisterSchema, 
                                    UserSchema)

# from .utils import send_verification_email, send_password_reset_email # You'll need to create these email utilities

router = Router()

@router.post("/register", response=UserSchema)
def register(request, payload: RegisterSchema):
    """Register a new user with username, email and password."""
    username_exists = User.objects.filter(
        username=payload.username
    ).exists()
    email_exists = User.objects.filter(
        email=payload.email
    ).exists()
    
    if username_exists or email_exists:
        raise HttpError(400, "Username or email already exists.")
    
    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        is_active=True # Deactivate until email is verified
    )
    # Create UserProfile only if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=user)  # type: ignore

    # send_verification_email(user) # Send an email with a token
    return {"id": user.id, "username": user.username, "email": user.email, "profile": profile}

@router.post("/login")
def login(request, payload: LoginSchema):
    """Authenticate user and return JWT tokens."""
    try:
        user = User.objects.get(username=payload.username)
        if not user.check_password(payload.password):
            raise HttpError(401, "Invalid credentials")
    except User.DoesNotExist:
        raise HttpError(401, "Invalid credentials")

    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

@router.post("/token/refresh")
def token_refresh(request, payload: RefreshSchema):
    """Get a new access and refresh token (token rotation)."""
    try:
      refresh = RefreshToken(payload.refresh)
      user_id = refresh.payload["user_id"]
      user = User.objects.get(id=user_id)
      new_refresh_token = RefreshToken.for_user(user)

      # Blacklist the used refresh token.
      # Requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS.
      refresh.blacklist()

      return {
        "refresh": str(new_refresh_token),
        "access": str(new_refresh_token.access_token),
      }
    except Exception:
      # Catches TokenError, User.DoesNotExist, and errors from blacklist()
        raise HttpError(401, "Invalid or expired refresh token")



@router.get("/profile", auth=JWTAuth(), response=UserSchema)
def get_profile(request):
    """Get the authenticated user's profile."""
    user = request.auth
    profile, created = UserProfile.objects.get_or_create(user=user)
    return {"id": user.id, "username": user.username, "email": user.email, "profile": profile}

@router.post("/profile/set-pin", auth=JWTAuth())
def set_pin(request, payload: PinSchema):
    """Set or update the user's PIN."""
    profile, _ = UserProfile.objects.get_or_create(user=request.auth)
    profile.set_pin(payload.pin)
    profile.save()
    return {"message": "PIN has been set successfully."}
