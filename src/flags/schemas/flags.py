import re
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, field_validator


class CreateFlagRequest(BaseModel):
    key: str
    name: str = Field(min_length=3)
    is_active: bool = Field(True)

    @field_validator("key", mode="after")
    def validate_key_format(self, key: str) -> "CreateFlagRequest":
        match = re.match(r"[a-z\-]{3,}", key)
        if len(key) != len(match.string):
            raise ValidationError(
                "String must be at least 3 characters long and only contain lowercase letters or hyphens"
            )
        return self


class GetFlagResponse(BaseModel):
    id: UUID
    key: str
    name: str
    is_active: bool
