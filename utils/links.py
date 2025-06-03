from random import randint
from sqlalchemy import select
from database import models
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
import secrets
import string

async def generate_short_link(original_url: str, db_session: AsyncSession) -> str:
    """
    Generate a short link for the given original URL.
    """
    short_link = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(randint(5, 10)))
    r = (await db_session.execute(select(models.Link).filter(models.Link.link == short_link))).scalar_one_or_none()
    if not r:
        return short_link
    else:
        return await generate_short_link(original_url, db_session)

async def check_expired(link: models.Link) -> bool:
    """
    Check if the given link has expired.
    """
    if link.expired_at is None:
        return False
    return link.expired_at < datetime.datetime.now(datetime.timezone.utc)
