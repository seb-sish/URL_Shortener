from random import randint
from sqlalchemy import func, select
from database import models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
import datetime
import secrets
import string


async def generate_short_link(original_url: str, db_session: AsyncSession) -> str:
    """
    Generate a short link for the given original URL.
    """
    short_link = "".join(secrets.choice(
        string.ascii_uppercase + string.digits) for _ in range(randint(5, 10)))
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
    exp_t = link.expired_at.replace(tzinfo=datetime.timezone.utc)
    cur_t = datetime.datetime.now(datetime.timezone.utc)
    return exp_t < cur_t


async def add_click(link: models.Link, request: Request, db_session: AsyncSession) -> None:
    """
    Add a click record for the given link.
    """
    click = models.Click(
        link_id=link.id,
        user_agent=request.headers.get("User-Agent"),
        ip=request.client.host
    )
    db_session.add(click)
    await db_session.commit()


async def get_link_stats(link: models.Link, db_session: AsyncSession) -> dict:
    """
    Get statistics for the given link.
    """
    stats = {
        "last_hours_clicks": 0,
        "last_day_clicks": 0,
        "last_week_clicks": 0
    }

    now = datetime.datetime.now(datetime.timezone.utc)
    # all_clicks = await db_session.execute(
    #     select(models.Click).filter(models.Click.link_id == link.id)
    # )

    # Calculate clicks in the last hour
    last_hour = now - datetime.timedelta(hours=1)
    stats["last_hours_clicks"] = (await db_session.execute(
        select(func.count(models.Click.id))
        .filter(
            models.Click.link_id == link.id,
            models.Click.created_at >= last_hour
        )
    )).scalar()

    # Calculate clicks in the last day
    last_day = now - datetime.timedelta(days=1)
    stats["last_day_clicks"] = (await db_session.execute(
        select(func.count(models.Click.id))
        .filter(
            models.Click.link_id == link.id,
            models.Click.created_at >= last_day
        )
    )).scalar()

    # Calculate clicks in the last week
    last_week = now - datetime.timedelta(weeks=1)
    stats["last_week_clicks"] = (await db_session.execute(
        select(func.count(models.Click.id))
        .filter(
            models.Click.link_id == link.id,
            models.Click.created_at >= last_week
        )
    )).scalar()

    return stats
