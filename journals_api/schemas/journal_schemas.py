from ninja import Schema
from datetime import datetime
from typing import Optional
from enum import Enum

# === Input Schemas ===
class JournalCreateSchema(Schema):
    """
    Schema for creating a journal entry.
    """
    class MoodTag(str, Enum):
        MERRY = "MERRY"
        GLOOMY = "GLOOMY"
        COVERT = "COVERT"

    title: str
    content: str
    mood_tag: MoodTag

class JournalUpdateSchema(Schema):
    """
    Schema for updating a journal entry.
    """
    title: Optional[str] = None
    content: Optional[str] = None
    mood_tag: Optional[str] = None

class TweetInspoSchema(Schema):
    """
    Schema for tweet inspiration.
    """
    twitter_handle: str

# === Output Schemas ===
class JournalOutSchema(Schema):
    """
    Schema for journal output.
    """
    id: int
    title: str
    content: Optional[str] = None # Content is hidden for covert journals by default
    date_added: datetime
    mood_tag: str
    is_covert: bool # A flag for the frontend

class TweetUrlSchema(Schema):
    """
    Schema for tweet URL.
    """
    tweet_url: str

class ImageUploadOutSchema(Schema):
    """
    Schema for image upload output.
    """
    image_url: str
    markdown_code: str

class ErrorSchema(Schema):
    """
    Schema for errors
    """
    error: str