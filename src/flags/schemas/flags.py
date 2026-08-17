import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CreateFlagRequest(BaseModel):
    key: str
    name: str = Field(min_length=3)
    is_active: bool = Field(True)

    @field_validator("key", mode="after")
    @classmethod
    def validate_key_format(cls, key: str) -> str:
        if not re.fullmatch(r"[a-z\-]{3,}", key):
            raise ValueError(
                "key must be at least 3 characters long and contain only lowercase letters or hyphens"
            )
        return key


class GetFlagResponse(BaseModel):
    id: UUID
    key: str
    name: str
    is_active: bool
