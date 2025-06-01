from pydantic import BaseModel

from schemas import LinkGetSchema

class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str

class UserGetSchema(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    links: list[LinkGetSchema]


