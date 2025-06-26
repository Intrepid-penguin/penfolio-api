from typing import List
from django.http import JsonResponse
from ninja import Router, File
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.pagination import paginate, PageNumberPagination
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from django.db.models import Q

from journals_api.schemas.user_schemas import PinSchema
from ..models.journals_model import Journal
from ..schemas.journal_schemas import JournalCreateSchema, JournalUpdateSchema, JournalOutSchema, ImageUploadOutSchema
from ..utils import update_streak_on_creation # Your business logic utilities
import cloudinary.uploader

router = Router(auth=JWTAuth()) # Apply authentication to all routes in this router

@router.get("/", response=List[JournalOutSchema])
@paginate(PageNumberPagination, page_size=5)
def list_journals(request, mood_tag: str = None):
    """List journals for the authenticated user, optionally filtered by mood tag."""
    user = request.auth
    queryset = Journal.objects.filter(owner=user)
    
    # Exclude covert journals unless specifically requested with a PIN via a different endpoint
    if mood_tag and mood_tag != 'COVERT':
        queryset = queryset.filter(mood_tag=mood_tag)
    else:
        queryset = queryset.exclude(mood_tag='COVERT')

    journals = queryset.order_by('-date_added')
    # Set is_covert field for each journal
    for journal in journals:
        journal.is_covert = (journal.mood_tag == 'COVERT')

    return journals

@router.post("/covert", response=List[JournalOutSchema])
@paginate(PageNumberPagination, page_size=5)
def list_covert_journals(request, payload: PinSchema):
    """List covert journals for the authenticated user after PIN verification."""
    
    profile = request.auth.user_profile
    if not profile.check_pin(payload.pin):
        raise HttpError(403,"Incorrect PIN")
        
    journals = Journal.objects.filter(owner=request.auth, mood_tag='COVERT').order_by('-date_added')
    # Set is_covert field for each journal
    for journal in journals:
        journal.is_covert = True
        
    return journals

@router.get("/{journal_id}", response=JournalOutSchema)
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
    return journal

@router.post("/{journal_id}/reveal", response=JournalOutSchema)
def reveal_covert_journal(request, journal_id: int, payload: PinSchema):
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    if journal.mood_tag != 'CO':
        return {"error": "This is not a covert journal."}, 400
        
    if not request.auth.user_profile.check_pin(payload.pin):
        return {"error": "Incorrect PIN"}, 403
        
    return journal

@router.post("/", response=JournalOutSchema)
def create_journal(request, payload: JournalCreateSchema):
    """Create a new journal entry for the authenticated user."""
    user = request.auth
    if payload.mood_tag == 'COVERT' and not user.user_profile.pin:
        return {"error": "You must set a PIN in your profile to create a Covert journal."}, 403

    journal = Journal.objects.create(owner=user, **payload.dict())
    update_streak_on_creation(user) # Your streak logic
    journal.is_covert = (journal.mood_tag == 'CO')
    return journal

@router.put("/{journal_id}", response=JournalOutSchema)
def update_journal(request, journal_id: int, payload: JournalUpdateSchema):
    """Update an existing journal entry for the authenticated user."""
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(journal, attr, value)
    journal.save()
    journal.is_covert = (journal.mood_tag == 'COVERT')
    return journal

@router.delete("/{journal_id}")
def delete_journal(request, journal_id: int):
    journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
    journal.delete()
    return {"status": "successfull"}

@router.get("/search/", response=List[JournalOutSchema])
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
    print(results)
    # Set is_covert field for each journal
    for journal in results:
        journal.is_covert = False
    return results

# @router.post(response=TweetUrlSchema, path="/{journal_id}/tweet")
# def tweet_journal(request, journal_id: int, payload: TweetInspoSchema):
#     journal = get_object_or_404(Journal, id=journal_id, owner=request.auth)
#     if journal.mood_tag == 'CO':
#         return {"detail": "You cannot tweet a covert journal."}, 403
    
#     x_user_tweet = get_twitter_inspo(payload.twitter_handle)
#     if x_user_tweet is None:
#         return {"detail": f"Could not find tweets for user {payload.twitter_handle}"}, 404

#     tweet_text = generate_tweet(x_user_tweet, journal.content)
#     tweet_url = f"https://twitter.com/intent/tweet?text={urlencode({'text': tweet_text})}"
#     return {"tweet_url": tweet_url}

@router.post("/upload-image", response=ImageUploadOutSchema)
def upload_image(request, file: UploadedFile = File(...)):
    # Configure Cloudinary as before
    result = cloudinary.uploader.upload(file)
    image_url = result['secure_url']
    return {
        "image_url": image_url,
        "markdown_code": f"![alt text]({image_url})"
    }
