from datetime import datetime
from pydantic import BaseModel, HttpUrl
from sqlalchemy import false


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

    last_hours_clicks: int = 0
    last_day_clicks: int = 0
    last_week_clicks: int = 0

    class Config:
        from_attributes = True
    
