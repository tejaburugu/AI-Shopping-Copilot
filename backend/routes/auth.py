from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.auth import TokenResponse, UserCreate, UserLogin, UserPublic
from services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_db,
)
from models.db import UserTable

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user: UserTable) -> TokenResponse:
    token = create_access_token(subject=str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserPublic(id=user.id, email=user.email, full_name=user.full_name),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_db)):
    user = await create_user(session, payload)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(session, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_response(user)


@router.get("/me", response_model=UserPublic)
async def me(current_user: UserTable = Depends(get_current_user)):
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
    )
