from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBasic, 
    HTTPBasicCredentials,
)

from database import models, get_session
from utils import verify_password, hash_password, config
from schemas import *

security = HTTPBasic()
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CredentialsDep = Annotated[HTTPBasicCredentials, Depends(security)]

authRouter = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"detail": "Not found"}}
)

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
        return None
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


@authRouter.post("/register", response_model=UserGetSchema)
async def register(
    response: Response,
    db_session: SessionDep,
    user_data: UserCreateSchema
) -> UserGetSchema:
    if await get_user(db_session, user_data.username, user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Username or Email already taken",
                            headers={"WWW-Authenticate": "Basic"})
    else:
        user = await create_user(db_session, user_data)
        if not user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to create user")
        
        response.status_code = status.HTTP_201_CREATED
        response.headers["Authorization"] = f"Basic {user.id}"
        return UserGetSchema.model_validate(user)


@authRouter.post("/login", response_model=UserGetSchema)
async def login(
    db_session: SessionDep,
    credentials: CredentialsDep
) -> UserGetSchema:
    user = await authenticate_user(
        db_session, credentials
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password",
                            headers={"WWW-Authenticate": "Basic"})
    return UserGetSchema.model_validate(user)

@authRouter.get("/me")
async def me(
    user: Annotated[models.User, Depends(authenticate_user)]
) -> UserGetSchema:
    return UserGetSchema.model_validate(user)
