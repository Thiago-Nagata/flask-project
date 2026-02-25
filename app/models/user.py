from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId

class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    username: str

class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    username: str
    password: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
