import datetime
from pydantic import BaseModel, EmailStr

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserGetSchema(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime
    is_admin: bool

    class Config:
        from_attributes = True
