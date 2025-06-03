from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List

import datetime
from database import models, get_session
from utils import generate_short_link
from schemas import *

from api.dependenses import SessionDep, UserDep

privateRouter = APIRouter(
    prefix="/urls",
    tags=["link"],
    responses={
        401: {"detail": "Unauthorized"},
        404: {"detail": "Url not found"}
    }
)

@privateRouter.get("")
async def my_short_links(
        user: UserDep,
        session: SessionDep
    ) -> List[LinkGetSchema]:
    """
    Get account created short links.
    """

    links = await session.execute(
        select(models.Link).where(models.Link.owner_id == user.id)
    )
    return [LinkGetSchema.model_validate(i) for i in links.scalars().all()]

@privateRouter.post("")
async def create_short_link(
        url: LinkCreateSchema,
        user: UserDep,
        session: SessionDep
    ) -> LinkGetSchema:
    """
    Create a short link for the given original URL.
    """

    short_link = await generate_short_link(url.original_link, session)
    new_link = models.Link(
        link=short_link,
        original_link=url.original_link,
        owner_id=user.id,
        expired_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=url.expire_days) if url.expire_days else None,
    )
    session.add(new_link)
    await session.commit()
    await session.refresh(new_link)
 
    return new_link