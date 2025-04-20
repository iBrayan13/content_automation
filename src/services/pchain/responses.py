from typing import Any

from pydantic import BaseModel

class Response(BaseModel):
    """Generic response model for chain outputs"""

    response: (
        str | BaseModel | Any
    )  # Updated to accept both string and BaseModel responses
    error: str | None = None
    metadata: dict[Any, Any] | None = None
