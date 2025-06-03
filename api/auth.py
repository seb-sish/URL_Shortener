from fastapi import APIRouter, HTTPException, Response, status
from fastapi import HTTPException, status
from schemas import *

from api.dependenses import (
    SessionDep, CredentialsDep, UserDep, 
    get_user, authenticate_user, create_user)

authRouter = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        401: {"detail": "Unauthorized"},
        404: {"detail": "Not found"}
    }
)

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
        response.headers["Authorization"] = "Basic"
        return UserGetSchema.model_validate(user)


@authRouter.post("/login", response_model=UserGetSchema)
async def login(
    db_session: SessionDep,
    credentials: CredentialsDep
) -> UserGetSchema:
    user = await authenticate_user(
        db_session, credentials
    )
    return UserGetSchema.model_validate(user)
    
@authRouter.get("/me")
async def get_info_about_me(
    user: UserDep
) -> UserGetSchema:
    return UserGetSchema.model_validate(user)
