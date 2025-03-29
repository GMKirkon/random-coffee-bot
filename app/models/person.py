from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core.core_schema import str_schema
        return str_schema()

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value) and not isinstance(value, ObjectId):
            raise ValueError("Invalid ObjectId")
        return str(value)

class Person(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "tags": ["developer", "python"],
                "created_at": "2024-03-29T12:00:00"
            }
        }
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)