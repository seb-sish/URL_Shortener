from fastapi import APIRouter, HTTPException, Query, Response, status

from sqlalchemy import select
from typing import List

from datetime import datetime, timedelta, timezone
from database import models
from schemas.link import LinkGetStatusSchema
from utils import generate_short_link, check_expired, get_link_stats
from schemas import *

from api.dependencies import SessionDep, UserDep

privateRouter = APIRouter(
    prefix="/urls",
    tags=["link"],
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "You do not have permission to access this resource"},
        404: {"detail": "Url not found"}
    }
)


@privateRouter.get("")
async def my_short_links(
    user: UserDep,
    session: SessionDep,
    limit: int = Query(50, ge=0),
    offset: int = Query(0, ge=0)
) -> List[LinkGetSchema]:
    """
    Get account created short links.
    """
    if limit > 100:
        limit = 100
    links = await session.execute(
        select(models.Link).filter(models.Link.owner_id ==
                                   user.id).limit(limit).offset(offset)
    )
    return [LinkGetSchema.model_validate(i) for i in links.scalars().all()]


@privateRouter.post("")
async def create_short_link(
    url: LinkCreateSchema,
    user: UserDep,
    session: SessionDep,
    response: Response
) -> LinkGetSchema:
    """
    Create a short link for the given original URL.
    """

    short_link = await generate_short_link(url.original_link, session)
    new_link = models.Link(
        link=short_link,
        original_link=url.original_link,
        owner_id=user.id,
        expired_at=datetime.now(
            timezone.utc) + timedelta(days=url.expire_days) if url.expire_days else None,
    )
    session.add(new_link)
    await session.commit()
    await session.refresh(new_link)

    response.status_code = status.HTTP_201_CREATED
    return new_link


@privateRouter.get("/status")
async def get_all_me_short_link_status(
    user: UserDep,
    session: SessionDep,
    limit: int = Query(50, ge=0),
    offset: int = Query(0, ge=0)
) -> List[LinkGetStatusSchema]:
    """
    Get the status of all short links for the authenticated user.
    """
    if limit > 100:
        limit = 100
    db_links = (await session.execute(
        select(models.Link).filter(models.Link.owner_id ==
                                   user.id).limit(limit).offset(offset)
    )).scalars().all()
    return [LinkGetStatusSchema(link=db_link.link, activated=db_link.activated,
                                expired=await check_expired(db_link), expired_at=db_link.expired_at) for db_link in db_links]


@privateRouter.get("/stats")
async def get_all_me_short_link_stats(
    user: UserDep,
    session: SessionDep,
    limit: int = Query(50, ge=0),
    offset: int = Query(0, ge=0)
) -> List[LinkGetSchemaWithStats]:
    """
    Get the statistics of all short links for the authenticated user.
    """
    if limit > 100:
        limit = 100
    db_links = (await session.execute(
        select(models.Link).filter(models.Link.owner_id ==
                                   user.id).limit(limit).offset(offset)
    )).scalars().all()

    schemStats = []
    for db_link in db_links:
        stats = LinkGetSchemaWithStats.model_validate(db_link)
        stats.last_hours_clicks, stats.last_day_clicks, stats.last_week_clicks = (await get_link_stats(db_link, session)).values()
        schemStats.append(stats)
    schemStats.sort(key=lambda x: x.last_hours_clicks +
                    x.last_day_clicks + x.last_week_clicks, reverse=True)
    return schemStats


@privateRouter.get("/{url_key}")
async def get_my_short_link(
    url_key: str,
    user: UserDep,
    session: SessionDep
) -> LinkGetSchema:
    """
    Get a specific short link created by the user.
    """
    url_key = url_key.strip().upper()
    db_link = (await session.execute(
        select(models.Link).filter(models.Link.link == url_key)
    )).scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    elif db_link.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to access this link")

    return LinkGetSchema.model_validate(db_link)


@privateRouter.get("/{url_key}/status")
async def get_short_link_status(
    url_key: str,
    user: UserDep,
    session: SessionDep
) -> LinkGetStatusSchema:
    """
    Get the status of a short link for the given URL key.
    """
    url_key = url_key.strip().upper()
    db_link = (await session.execute(
        select(models.Link).filter(models.Link.link == url_key)
    )).scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    elif db_link.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to access this link")

    return LinkGetStatusSchema(link=db_link.link, activated=db_link.activated, expired=await check_expired(db_link), expired_at=db_link.expired_at)


@privateRouter.put("/{url_key}/status")
async def update_short_link_status(
    url_key: str,
    activated: bool,
    user: UserDep,
    session: SessionDep
) -> LinkGetSchema:
    """
    Update the status of a short link for the given URL key.
    """
    url_key = url_key.strip().upper()
    db_link = (await session.execute(
        select(models.Link).filter(models.Link.link == url_key)
    )).scalar_one_or_none()

    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    elif db_link.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update this link")

    elif db_link.activated == activated:
        if activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Link is already activated")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Link is already deactivated")

    db_link.activated = activated
    await session.commit()
    await session.refresh(db_link)
    return LinkGetSchema.model_validate(db_link)


@privateRouter.get("/{url_key}/stats")
async def get_short_link_stats(
    url_key: str,
    user: UserDep,
    session: SessionDep
) -> LinkGetSchemaWithStats:
    """
    Get the statistics of a short link for the given URL key.
    """
    url_key = url_key.strip().upper()
    db_link = (await session.execute(
        select(models.Link).filter(models.Link.link == url_key)
    )).scalar_one_or_none()
    if not db_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    elif db_link.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to access this link")

    stats = LinkGetSchemaWithStats.model_validate(db_link)
    stats.last_hours_clicks, stats.last_day_clicks, stats.last_week_clicks = (await get_link_stats(db_link, session)).values()
    return stats
