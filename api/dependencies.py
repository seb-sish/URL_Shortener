
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
)
from typing import Annotated

from utils import verify_password, hash_password, config
from database import models, get_session
from schemas import *

security = HTTPBasic()

CredentialsDep = Annotated[HTTPBasicCredentials, Depends(security)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_user(db_session: AsyncSession, username: str, email: str = None) -> models.User | None:
    if email:
        user = (await db_session.execute(
            select(models.User)
            .filter(or_(
                models.User.username == username,
                models.User.email == email
            ))
        )).scalar_one_or_none()
    else:
        user = (await db_session.execute(
            select(models.User).filter(models.User.username == username)
        )).scalar_one_or_none()
    return user


async def authenticate_user(
    db_session: SessionDep,
    credentials: CredentialsDep
) -> models.User | None:
    user = await get_user(db_session, credentials.username)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password",
                            headers={"WWW-Authenticate": "Basic"})
    return user


async def create_user(
    db_session: SessionDep,
    user_data: UserCreateSchema
) -> models.User | None:
    user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def user_is_admin(
    db_session: SessionDep,
    credentials: CredentialsDep
) -> models.User | None:
    user = await get_user(db_session, credentials.username)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password",
                            headers={"WWW-Authenticate": "Basic"})
    elif not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to access this resource")
    return user


UserDep = Annotated[models.User, Depends(authenticate_user)]
AdminDep = Annotated[models.User, Depends(user_is_admin)]
