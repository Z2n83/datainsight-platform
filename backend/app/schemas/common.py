"""
Common Pydantic schemas for API responses.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    code: int = 0
    message: str = "success"
    data: Any = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    code: int
    message: str
    data: Any = None
