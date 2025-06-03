from datetime import datetime
from pydantic import BaseModel, HttpUrl


class LinkCreateSchema(BaseModel):
    original_link: HttpUrl
    expire_days: int | None = None
    

class LinkGetSchema(BaseModel):
    id: int
    link: str
    original_link: HttpUrl
    activated: bool
    created_at: datetime
    expired_at: datetime | None 
    owner_id: int
    class Config:
        from_attributes = True
    

class LinkGetSchemaWithStats(LinkGetSchema):
    last_hours_clicks: int = 0
    last_day_clicks: int = 0
    last_week_clicks: int = 0

class LinkGetStatusSchema(BaseModel):
    link: str
    activated: bool
    expired: bool
    expired_at: datetime | None = None

