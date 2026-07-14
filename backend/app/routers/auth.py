from fastapi import APIRouter, Depends, HTTPException
import logging

from app.context import set_user_id
from app.dependencies.auth import get_current_user
from app.models.user import TokenResponse, UserCreate, UserLogin, UserPublic
from app.services.auth_service import login_user, register_user
from app.services.settings_service import settings_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(body: UserCreate):
    try:
        user, token = register_user(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    set_user_id(user.id)
    try:
        settings_repository.ensure_provider_defaults()
    except Exception:
        logger.exception("provider_seed_after_register_failed user=%s", user.id)
    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    try:
        user, token = login_user(body)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    set_user_id(user.id)
    try:
        settings_repository.ensure_provider_defaults()
    except Exception:
        logger.exception("provider_seed_after_login_failed user=%s", user.id)
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=UserPublic)
async def me(user: UserPublic = Depends(get_current_user)):
    return user
