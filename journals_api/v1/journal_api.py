from typing import List

import cloudinary.uploader
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import File, Query, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja_jwt.authentication import JWTAuth

from journals_api.schemas.base_schema import ResponseSchema
from journals_api.schemas.user_schemas import PinSchema
from journals_api.v1.utils import CustomPageNumberPagination, create_api_response

from ..models.journals_model import Journal
from ..schemas.journal_schemas import (ImageUploadOutSchema,
                                       JournalCreateSchema, JournalOutSchema,
                                       JournalUpdateSchema, PaginatedResponse)
from ..utils import update_streak_on_creation

router = Router(auth=JWTAuth())


@router.get(
    "/",
    response=
        ResponseSchema[
            PaginatedResponse[
                JournalOutSchema
            ]
        ],
)
def list_journals(
    request,
    pagination: CustomPageNumberPagination.Input = Query(...),
    mood_tag: str = None,
):
    """
    List journals for the authenticated user,
    optionally filtered by mood tag.
    """
    user = request.auth
    queryset = Journal.objects.filter(
        owner=user
    )

    if mood_tag and mood_tag.upper() != "COVERT":
        queryset = queryset.filter(
            mood_tag=mood_tag
        )
    else:
        queryset = queryset.exclude(
            mood_tag="COVERT"
        )

    ordered_queryset = queryset.order_by(
        "-date_added"
    )
    
    paginator = CustomPageNumberPagination()

    response_data = paginator.paginate_queryset(
        queryset=ordered_queryset,
        pagination_in=pagination,
        message="Journals retrieved successfully",
    )

    items = response_data.get("items", [])
    for journal in items:
        journal.is_covert = (getattr(journal, "mood_tag", None) == "COVERT")

    return create_api_response(response_data, message="Journals retrieved successfully", status_code=200)


@router.post("/covert", 
    response=ResponseSchema[
            PaginatedResponse[
                JournalOutSchema
            ]
        ],)
def list_covert_journals(request,  payload: PinSchema, pagination: CustomPageNumberPagination.Input = Query(...)):
    """List covert journals for the authenticated user after PIN verification."""
    queryset = Journal.objects.filter(
        owner=request.auth,
        mood_tag="COVERT"
    )
    try:
        profile = request.auth.user_profile
        if not profile.check_pin(payload.pin):
            raise HttpError(403, "Incorrect PIN")
    except AttributeError:
        raise HttpError(403, "User profile not found, cannot check PIN.")
        
    ordered_queryset = queryset.order_by(
        "-date_added"
    )
    
    paginator = CustomPageNumberPagination()

    response_data = paginator.paginate_queryset(
        queryset=ordered_queryset,
        pagination_in=pagination,
        message="Journals retrieved successfully",
    )

    items = response_data.get("items", [])
    for journal in items:
        journal.is_covert = (getattr(journal, "mood_tag", None) == "COVERT")
        
    return create_api_response(response_data, message="Journal retrieved", status_code=200)

@router.get("/{journal_id}", response=ResponseSchema[JournalOutSchema])
def get_journal(request, journal_id: int):
    """Get a specific journal entry for the authenticated user."""
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    
    # For covert journals, don't return content. The frontend must call /reveal
    if journal.mood_tag == 'COVERT':
        return JournalOutSchema(
            id=journal.id,
            title=journal.title,
            date_added=journal.date_added,
            mood_tag='COVERT',
            is_covert=True,
        )
    
    # Set is_covert field for non-covert journals
    journal.is_covert = False
    return create_api_response(journal, message="Journal retrieved", status_code=200)

@router.post("/{journal_id}/reveal", response=ResponseSchema[JournalOutSchema])
def reveal_covert_journal(request, journal_id: int, payload: PinSchema):
    """Reveals the content of a specific covert journal after PIN verification."""
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    if journal.mood_tag != 'COVERT':
        raise HttpError(400, "This is not a covert journal.")
        
    try:
        profile = request.auth.user_profile
        if not profile.check_pin(payload.pin):
            raise HttpError(403, "Incorrect PIN")
    except AttributeError:
        raise HttpError(403, "User profile not found, cannot check PIN.")
    
    journal.is_covert = (journal.mood_tag == 'COVERT')
        
    return create_api_response(journal, message="Journal retrieved", status_code=200)

@router.post("/", response=ResponseSchema[JournalOutSchema])
def create_journal(request, payload: JournalCreateSchema):
    """Create a new journal entry for the authenticated user."""
    user = request.auth
    if payload.mood_tag == 'COVERT':
        try:
            if not user.user_profile.pin:
                raise HttpError(403, "A PIN must be set in your profile to create a Covert journal.")
        except AttributeError:
            raise HttpError(403, "User profile not found. Cannot create a Covert journal.")

    journal = Journal.objects.create(owner=user, **payload.dict())
    update_streak_on_creation(user) # Your streak logic
    journal.is_covert = (journal.mood_tag == 'COVERT')
    return create_api_response(journal, message="Created", status_code=201) #201, journal

@router.put("/{journal_id}", response=ResponseSchema[JournalOutSchema])
def update_journal(request, journal_id: int, payload: JournalUpdateSchema):
    """Update an existing journal entry for the authenticated user."""
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    
    # If changing mood_tag to COVERT, check for PIN
    if payload.mood_tag == 'COVERT' and journal.mood_tag != 'COVERT':
        try:
            if not request.auth.user_profile.pin:
                raise HttpError(403, "A PIN must be set in your profile to set a journal as Covert.")
        except AttributeError:
            raise HttpError(403, "User profile not found. Cannot set journal as Covert.")

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(journal, attr, value)
    journal.save()
    journal.is_covert = (journal.mood_tag == 'COVERT')
    return create_api_response(journal, message="Journal updated", status_code=200)

@router.delete("/{journal_id}", response={204: None})
def delete_journal(request, journal_id: int):
    """Delete a specific journal entry for the authenticated user."""
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    journal.delete()
    return 204, None

@router.get("/search/", response=ResponseSchema[List[JournalOutSchema]])
def search_journals(request, q: str = None):
    """Search journals by title or content for the authenticated user, excluding covert journals."""
    if not q:
        return []
    query = Q(title__icontains=q) | Q(content__icontains=q)
    results = Journal.objects.filter(
        query,
        owner=request.auth
    ).exclude(
        mood_tag='COVERT'
    ).distinct()

    # Set is_covert field for each journal
    for journal in results:
        journal.is_covert = False
    return create_api_response(results, message="Search results retrieved", status_code=200)


@router.post("/upload-image", response=ImageUploadOutSchema)
def upload_image(request, file: UploadedFile = File(...)):
    """Uploads an image to Cloudinary and returns the URL."""
    try:
        result = cloudinary.uploader.upload(file)
        image_url = result.get('secure_url')
        if not image_url:
            raise HttpError(500, "Image upload failed: Cloudinary did not return a secure URL.")
        
        return {
            "image_url": image_url,
            "markdown_code": f"![alt text]({image_url})"
        }
    except cloudinary.exceptions.Error as exc:
        # Log the actual error for debugging, but return a generic message to the user.
        raise HttpError(503, "Image upload service is currently unavailable.") from exc
    except Exception as exc:
        # Catch any other unexpected errors during the upload process.
        raise HttpError(500, "An unexpected error occurred during image upload.") from exc

