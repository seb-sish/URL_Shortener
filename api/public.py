from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from database import models, get_session
from schemas import *

SessionDep = Annotated[AsyncSession, Depends(get_session)]

publicRouter = APIRouter(
    prefix="",
    tags=["link"],
    responses={404: {"detail": "Url not found"}},
    dependencies=[Depends(get_session)]
)

@publicRouter.get("/{url_key}")
async def forward_to_target_url(
        url_key: str,
        session: SessionDep
    ):
    async with session as db_session:
        db_url = (await db_session.execute(
            select(models.Link)
            .filter(models.Link.link == url_key)
        )).scalar_one_or_none()

    if db_url:
        return RedirectResponse(db_url.original_link)
    else:
        raise HTTPException(
            status_code=404,
            detail="Url not found"
        )