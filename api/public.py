from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from database import models
from schemas import *

from utils import check_expired
from api.dependenses import SessionDep
from utils.links import add_click

publicRouter = APIRouter(
    prefix="",
    tags=["link"],
    responses={404: {"detail": "Url not found"}}
)

@publicRouter.get("/{url_key}")
async def forward_to_target_url(
        url_key: str,
        request: Request,
        session: SessionDep
    ):
    url_key = url_key.strip().upper()
    async with session as db_session:
        db_url = (await db_session.execute(
            select(models.Link)
            .filter(models.Link.link == url_key)
        )).scalar_one_or_none()

    if not db_url:
        raise HTTPException(
            status_code=404,
            detail="Url not found"
        )
    elif not db_url.activated:
        raise HTTPException(
            status_code=404,
            detail="Url is deactivated"
        )
    elif await check_expired(db_url):
        raise HTTPException(
            status_code=404,
            detail="Url is expired"
        )

    await add_click(db_url, request, db_session)
    return RedirectResponse(db_url.original_link)
