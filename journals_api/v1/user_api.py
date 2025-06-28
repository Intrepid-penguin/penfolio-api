from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken

from ..models.user_model import UserProfile
from ..schemas.user_schemas import (LoginSchema,
                                    PinSchema, RefreshSchema,
                                    RegisterSchema, UserProfileSchema,
                                    UserSchema)


router = Router()

@router.post("/register", response=UserSchema)
def register(request, payload: RegisterSchema):
    """Register a new user with username, email and password."""
    if User.objects.filter(Q(username=payload.username) | Q(email=payload.email)).exists():
        raise HttpError(400, "Username or email already exists.")

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=payload.username,
                email=payload.email,
                password=payload.password,
                is_active=True
            )
            profile, _ = UserProfile.objects.get_or_create(user=user)
    except IntegrityError as exc:
        raise HttpError(400, "Username or email already exists.") from exc

    return {"id": user.id, "username": user.username, "email": user.email, "profile": profile}

@router.post("/login")
def login(request, payload: LoginSchema):
    """Authenticate user and return JWT tokens."""
    # Use Django's standard authentication method
    user = authenticate(username=payload.username, password=payload.password)

    if user is None:
        # This handles incorrect credentials or inactive users
        raise HttpError(401, "Invalid credentials or user not active.")

    refresh = RefreshToken.for_user(user)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile": UserProfileSchema.from_orm(profile)
    }
    return {
        "user": user_data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

@router.post("/token/refresh")
def token_refresh(request, payload: RefreshSchema):
    """Get a new access and refresh token (token rotation)."""
    try:
        refresh = RefreshToken(payload.refresh)
        refresh.blacklist()
        user_id = refresh.payload["user_id"]
        user = User.objects.get(id=user_id)
        new_refresh_token = RefreshToken.for_user(user)

        return {
            "refresh": str(new_refresh_token),
            "access": str(new_refresh_token.access_token),
        }
    
    except User.DoesNotExist:
        # This case is unlikely if the token is valid but is good for robustness.
        raise HttpError(401, "User associated with this token not found.")



@router.get("/profile", auth=JWTAuth(), response=UserSchema)
def get_profile(request):
    """Get the authenticated user's profile."""
    user = request.auth
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return {"id": user.id, "username": user.username, "email": user.email, "profile": profile}

@router.post("/profile/set-pin", auth=JWTAuth())
def set_pin(request, payload: PinSchema):
    """Set or update the user's PIN."""
    profile, _ = UserProfile.objects.get_or_create(user=request.auth)
    profile.set_pin(payload.pin)
    profile.save()
    return {"message": "PIN has been set successfully."}
