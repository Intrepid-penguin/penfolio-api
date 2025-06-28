from typing import Generic, TypeVar
from ninja import Schema

T = TypeVar('T')

class ResponseSchema(Schema, Generic[T]):
    """Base schema for successful API responses.
    
    Provides common structure for success responses including:
    - status code
    - message
    - data payload
    """
    status_code: int = 200
    status: str = "success"
    message: str
    data: T
