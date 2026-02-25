from pydantic import BaseModel, Field

class LoginPayload(BaseModel):
    username: str
    password: str

class CreateUser(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str = Field(None, alias="_id")
    username: str