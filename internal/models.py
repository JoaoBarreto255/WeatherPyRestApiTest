"""Api output models"""

from pydantic import BaseModel

class UserOutput(BaseModel):
    id: int
    created_at: str
    requested_at: str | None
    processed_at: str | None
