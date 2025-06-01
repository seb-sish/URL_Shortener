from pydantic import BaseModel


class LinkCreateSchema(BaseModel):
    link: str
    original_link: str
    expire_days: int | None = None
    

class LinkGetSchema(BaseModel):
    id: int
    link: str
    original_link: str
    activated: bool
    expaired: bool    
    created_at: str
    expired_at: str | None = None
    owner_id: int

    last_hours_clicks: int = 0
    last_day_clicks: int = 0
    last_week_clicks: int = 0
    
