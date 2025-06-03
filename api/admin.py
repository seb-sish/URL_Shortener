from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List

from datetime import datetime, timedelta, timezone
from database import models, get_session
from schemas.link import LinkGetStatusSchema
from utils import generate_short_link, check_expired, get_link_stats
from schemas import *

from api.dependencies import SessionDep, AdminDep

adminRouter = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "You do not have permission to access this resource"},
        404: {"detail": "Url not found"}
    }
)

@adminRouter.get("/urls")
async def get_all_short_links(
        admin: AdminDep,
        session: SessionDep,
        limit: int = Query(500, ge=0),
        offset: int = Query(0, ge=0)
    ) -> List[LinkGetSchema]:
    """
    Get account created short links.
    """

    links = await session.execute(
        select(models.Link).limit(limit).offset(offset)
    )
    return [LinkGetSchema.model_validate(i) for i in links.scalars().all()]

@adminRouter.get("/urls/status")
async def get_link_status(
        admin: AdminDep,
        session: SessionDep,
        limit: int = Query(500, ge=0),
        offset: int = Query(0, ge=0)
    ) -> List[LinkGetStatusSchema]:
    """
    Get status of all short link.
    """
    db_links = (await session.execute(
        select(models.Link).limit(limit).offset(offset)
    )).scalars().all()
    return [LinkGetStatusSchema(link=db_link.link, activated=db_link.activated, 
                                expired=await check_expired(db_link), expired_at=db_link.expired_at) for db_link in db_links]

@adminRouter.get("/urls/stats")
async def get_all_short_link_stats(
        admin: AdminDep,
        session: SessionDep,
        limit: int = Query(500, ge=0),
        offset: int = Query(0, ge=0)
    ) -> List[LinkGetSchemaWithStats]:
    """
    Get the statistics of all short links.
    """
    db_links = (await session.execute(
        select(models.Link).limit(limit).offset(offset)
    )).scalars().all()

    schemStats = []
    for db_link in db_links:
        stats = LinkGetSchemaWithStats.model_validate(db_link)
        stats.last_hours_clicks, stats.last_day_clicks, stats.last_week_clicks = (await get_link_stats(db_link, session)).values()
        schemStats.append(stats)
    schemStats.sort(key=lambda x: x.last_hours_clicks + x.last_day_clicks + x.last_week_clicks, reverse=True)
    return schemStats

@adminRouter.get("/urls/{url_key}/status")
async def get_short_link_status(
        url_key: str,
        admin: AdminDep,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    return LinkGetStatusSchema(link=db_link.link, activated=db_link.activated, expired=await check_expired(db_link), expired_at=db_link.expired_at)

@adminRouter.get("/urls/{url_key}/stats")
async def get_short_link_stats(
        url_key: str,
        admin: AdminDep,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    return LinkGetSchemaWithStats.model_validate(db_link)

@adminRouter.put("/urls/{url_key}/status")
async def update_short_link_status(
        url_key: str,
        activated: bool,
        admin: AdminDep,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    elif db_link.activated == activated:
        if activated:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link is already activated")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link is already deactivated")

    db_link.activated = activated
    await session.commit()
    await session.refresh(db_link)
    return LinkGetSchema.model_validate(db_link)

@adminRouter.delete("/urls/{url_key}")
async def delete_short_link(
        url_key: str,
        admin: AdminDep,
        session: SessionDep
    ) -> Response:
    """
    Delete a short link by its URL key.
    """
    url_key = url_key.strip().upper()
    db_link = (await session.execute(
        select(models.Link).filter(models.Link.link == url_key)
    )).scalar_one_or_none()
    
    if not db_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    await session.delete(db_link)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@adminRouter.get("/users/{user_name}")
async def get_user(
        user_name: str,
        admin: AdminDep,
        session: SessionDep
    ) -> UserGetSchema:
    """
    Get user information by username.
    """
    db_user = (await session.execute(
        select(models.User).filter(models.User.username == user_name)
    )).scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserGetSchema.model_validate(db_user)

@adminRouter.get("/users/{user_id}")
async def get_user(
        user_id: int,
        admin: AdminDep,
        session: SessionDep
    ) -> UserGetSchema:
    """
    Get user information by user ID.
    """
    db_user = (await session.execute(
        select(models.User).filter(models.User.id == user_id)
    )).scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserGetSchema.model_validate(db_user)

@adminRouter.get("/users/{user_id}/urls")
async def get_user_short_links(
        user_id: int,
        admin: AdminDep,
        session: SessionDep,
        limit: int = Query(500, ge=0),
        offset: int = Query(0, ge=0)
    ) -> List[LinkGetSchema]:
    """
    Get all short links created by a specific user.
    """
    db_links = (await session.execute(
        select(models.Link).filter(models.Link.owner_id == user_id).limit(limit).offset(offset)
    )).scalars().all()
    return [LinkGetSchema.model_validate(db_link) for db_link in db_links]

@adminRouter.get("/users/{user_id}/urls/status")
async def get_user_short_link_status(
        user_id: int,
        admin: AdminDep,
        session: SessionDep,
        limit: int = Query(500, ge=0),
        offset: int = Query(0, ge=0)
    ) -> List[LinkGetStatusSchema]:
    """
    Get the status of all short links created by a specific user.
    """
    db_links = (await session.execute(
        select(models.Link).filter(models.Link.owner_id == user_id).limit(limit).offset(offset)
    )).scalars().all()
    
    return [LinkGetStatusSchema(link=db_link.link, activated=db_link.activated, 
                                expired=await check_expired(db_link), expired_at=db_link.expired_at) for db_link in db_links]

@adminRouter.get("/users/{user_id}/urls/stats")
async def get_user_short_link_stats(
        user_id: int,
        admin: AdminDep,
        session: SessionDep,
        limit: int = Query(500, ge=0),
        offset: int = Query(0, ge=0)
    ) -> List[LinkGetSchemaWithStats]:
    """
    Get the statistics of all short links created by a specific user.
    """
    db_links = (await session.execute(
        select(models.Link).filter(models.Link.owner_id == user_id).limit(limit).offset(offset)
    )).scalars().all()

    return [LinkGetSchemaWithStats.model_validate(db_link) for db_link in db_links]

@adminRouter.delete("/users/{user_id}/urls")
async def delete_user_short_links(
        user_id: int,
        admin: AdminDep,
        session: SessionDep
    ) -> Response:
    """
    Delete all short links created by a specific user.
    """
    await session.delete(
        select(models.Link).filter(models.Link.owner_id == user_id)
    )
    
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@adminRouter.delete("/users/{user_id}")
async def delete_user(
        user_id: int,
        admin: AdminDep,
        session: SessionDep
    ) -> Response:
    """
    Delete a user and all their short links.
    """
    user = (await session.execute(
        select(models.User).filter(models.User.id == user_id)
    )).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await session.delete(user)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)