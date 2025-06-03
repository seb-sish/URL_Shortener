from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing_extensions import Annotated

import datetime
from database import models, get_session
from utils import generate_short_link, hash_password, verify_password
from schemas import *

security = HTTPBasic()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
credentials = Annotated[HTTPBasicCredentials, Depends(security)]
privateRouter = APIRouter(
    prefix="/url",
    tags=["link"],
    responses={404: {"detail": "Url not found"}}
)

@privateRouter.post("")
async def create_short_link(
        url: LinkCreateSchema,
        credentials: credentials,
        session: SessionDep
    ) -> LinkGetSchema:
    """
    Create a short link for the given original URL.
    """

    hashed_pass = (await session.execute(
        select(models.User.password).filter(models.User.username == credentials.username)
    )).scalar_one_or_none()
    if not hashed_pass:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    is_correct_password = verify_password(
        credentials.password, hashed_pass)
    
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    short_link = await generate_short_link(url.original_link, session)
    new_link = models.Link(
        link=short_link,
        original_link=url.original_link,
        owner_id=1,  # Assuming a default owner ID for now
        expired_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=url.expire_days) if url.expire_days else None,
    )
    session.add(new_link)
    await session.commit()
    await session.refresh(new_link)
 
    return new_link
    
# @privateRouter.get("/users/me")
# def read_current_user(username: Annotated[str, Depends(get_current_username)]):
#     return {"username": username}