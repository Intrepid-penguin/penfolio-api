# your_project/pagination.py

from typing import Any, Optional, Dict
from ninja.conf import settings
from django.db.models import QuerySet
from ninja import Schema
from ninja.pagination import PaginationBase
from pydantic import Field

class CustomPageNumberPagination(PaginationBase):
    """
    A custom pagination class that formats the response according to the
    ApiResponse schema structure.
    
    This class is intended to be used MANUALLY within a view, not with the
    @paginate decorator.
    """
    class Input(Schema):
        page: int = Field(1, ge=1, description="Page number")
        page_size: Optional[int] = Field(5, ge=1, description="Number of items per page") # A default is good practice

    # The __init__ can be simplified if you pass the message from the view
    def __init__(self, page_size: int = 5, max_page_size: int = 100, **kwargs: Any):
        self.page_size = page_size
        self.max_page_size = max_page_size
        super().__init__(**kwargs)

    # ... (the _get_page_size method is unchanged) ...
    def _get_page_size(self, requested_page_size: Optional[int]) -> int:
        if requested_page_size is None:
            return self.page_size
        return min(requested_page_size, self.max_page_size)

    def paginate_queryset(
        self,
        queryset: QuerySet,
        pagination_in: Input,
        message: str = "Operation successful",
    ) -> Dict[str, Any]:
        
        page_size = self._get_page_size(pagination_in.page_size)
        offset = (pagination_in.page - 1) * page_size
        
        paginated_data = {
            "items": queryset[offset : offset + page_size],
            "count": self._items_count(queryset),
        }

        return paginated_data
    
def create_api_response(data, message="Request was successfully", status_code=200):
    """
    Creates a consistent API response dictionary.

    Args:
        data: The payload/data to be returned.
        message (str): A descriptive message about the outcome.
        status_code (int): The HTTP status code.

    Returns:
        dict: A formatted API response.
    """
    return {
        "status_code": status_code,
        "status": "success" if 200 <= status_code < 300 else "error",
        "message": message,
        "data": data,
    }