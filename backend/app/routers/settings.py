import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.errors import PyMongoError

from app.dependencies.auth import get_current_user
from app.models.user import UserPublic

from app.models.schemas import (
    ProviderId,
    ProviderConfig,
    ProviderConfigResponse,
    ProviderConfigUpdate,
    TestConnectionResponse,
    ModelOption,
)
from app.providers.factory import ProviderFactory
from app.services.encryption import encryption_service
from app.services.settings_service import settings_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _mongo_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, RuntimeError):
        msg = str(exc)
        if "MongoDB" in msg or "Authentication required" in msg:
            return HTTPException(status_code=503, detail=msg)
    if isinstance(exc, PyMongoError):
        logger.exception("mongodb_settings_error")
        return HTTPException(
            status_code=503,
            detail=(
                "Could not reach MongoDB. Check MONGODB_URI on Render and allow "
                "0.0.0.0/0 in Atlas Network Access."
            ),
        )
    logger.exception("settings_error")
    return HTTPException(
        status_code=500,
        detail="Settings failed to load. Check Render logs and MongoDB configuration.",
    )


def _build_response(provider_id: ProviderId, saved: ProviderConfig | None) -> ProviderConfigResponse:
    provider_class = ProviderFactory.get_provider_class(provider_id)
    meta = provider_class.metadata

    enabled = saved.enabled if saved else False
    model = saved.model if saved and saved.model else meta.default_model
    if provider_id == ProviderId.OPENROUTER:
        from app.providers.openrouter_provider import normalize_openrouter_model

        model = normalize_openrouter_model(model)
    if model not in meta.model_ids:
        model = meta.default_model
    has_key = bool(saved and saved.api_key)
    masked = encryption_service.mask_key(saved.api_key) if has_key else None

    return ProviderConfigResponse(
        provider_id=provider_id,
        name=meta.name,
        description=meta.description,
        enabled=enabled,
        api_key_masked=masked,
        has_api_key=has_key,
        model=model,
        available_models=[
            ModelOption(id=m.id, name=m.name, modality=m.modality)
            for m in meta.models
        ],
        base_url=saved.base_url if saved else meta.default_base_url,
    )


@router.get("/providers", response_model=list[ProviderConfigResponse])
async def list_providers(_user: UserPublic = Depends(get_current_user)):
    settings_repository.ensure_provider_defaults()
    saved = settings_repository.get_all_safe()
    providers: list[ProviderConfigResponse] = []
    for pid in ProviderId:
        try:
            providers.append(_build_response(pid, saved.get(pid)))
        except Exception:
            logger.exception("provider_response_failed provider=%s", pid.value)
            meta = ProviderFactory.get_provider_class(pid).metadata
            providers.append(
                ProviderConfigResponse(
                    provider_id=pid,
                    name=meta.name,
                    description=meta.description,
                    enabled=False,
                    has_api_key=False,
                    model=meta.default_model,
                    available_models=[
                        ModelOption(id=m.id, name=m.name, modality=m.modality)
                        for m in meta.models
                    ],
                    base_url=meta.default_base_url,
                )
            )
    return providers


@router.get("/providers/{provider_id}", response_model=ProviderConfigResponse)
async def get_provider(
    provider_id: ProviderId,
    _user: UserPublic = Depends(get_current_user),
):
    saved = settings_repository.get_all_safe().get(provider_id)
    if saved is None:
        try:
            saved = settings_repository.get(provider_id)
        except Exception:
            logger.exception("provider_get_failed provider=%s", provider_id.value)
    return _build_response(provider_id, saved)


@router.put("/providers/{provider_id}", response_model=ProviderConfigResponse)
async def update_provider(
    provider_id: ProviderId,
    update: ProviderConfigUpdate,
    _user: UserPublic = Depends(get_current_user),
):
    try:
        existing = settings_repository.get(provider_id)
    except Exception as exc:
        raise _mongo_http_error(exc) from exc
    provider_class = ProviderFactory.get_provider_class(provider_id)
    meta = provider_class.metadata

    api_key = update.api_key
    if not api_key and existing:
        api_key = existing.api_key

    if update.enabled and not api_key:
        raise HTTPException(status_code=400, detail="API key is required to enable a provider")

    if api_key:
        temp_provider = provider_class(api_key=api_key)
        valid, msg = temp_provider.validate_api_key(api_key)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)

    model = update.model or (existing.model if existing else meta.default_model)
    if provider_id == ProviderId.OPENROUTER:
        from app.providers.openrouter_provider import normalize_openrouter_model

        model = normalize_openrouter_model(model)
    if model not in meta.model_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model. Choose from: {meta.model_ids}",
        )

    config = ProviderConfig(
        provider_id=provider_id,
        enabled=update.enabled,
        api_key=api_key,
        model=model,
        base_url=update.base_url or (existing.base_url if existing else meta.default_base_url),
    )
    try:
        settings_repository.save(config)
    except Exception as exc:
        raise _mongo_http_error(exc) from exc
    return _build_response(provider_id, config)


class TestBody(BaseModel):
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None


@router.post("/providers/{provider_id}/test", response_model=TestConnectionResponse)
async def test_provider(
    provider_id: ProviderId,
    request: TestBody | None = None,
    _user: UserPublic = Depends(get_current_user),
):
    try:
        saved = settings_repository.get(provider_id)
    except Exception as exc:
        raise _mongo_http_error(exc) from exc
    provider_class = ProviderFactory.get_provider_class(provider_id)
    meta = provider_class.metadata

    api_key = None
    model = meta.default_model
    base_url = meta.default_base_url

    if request:
        if request.api_key:
            api_key = request.api_key
        if request.model:
            model = request.model
        if request.base_url:
            base_url = request.base_url

    if saved:
        if not api_key:
            api_key = saved.api_key
        if not (request and request.model) and saved.model:
            model = saved.model
        if not (request and request.base_url) and saved.base_url:
            base_url = saved.base_url

    if provider_id == ProviderId.OPENROUTER:
        from app.providers.openrouter_provider import normalize_openrouter_model

        model = normalize_openrouter_model(model)

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required to test connection")

    provider = provider_class(api_key=api_key, model=model, base_url=base_url)
    valid, msg = provider.validate_api_key(api_key)
    if not valid:
        return TestConnectionResponse(success=False, message=msg)

    result = await provider.test_connection()
    return TestConnectionResponse(
        success=result.success,
        message=result.message,
        latency_ms=result.latency_ms,
    )
