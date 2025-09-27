"""Health check routes."""

import logging

from fastapi import APIRouter, Depends

from ...core.compliance import compliance_manager
from ...schemas.trending import ComplianceInfo, HealthResponse, ProviderInfo
from ..deps import get_trends_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check(service=Depends(get_trends_service)):
    """Health check endpoint."""
    try:
        provider_health = {}
        overall_status = "ok"

        for name, provider in service.providers.items():
            try:
                is_healthy = await provider.health_check()
                provider_health[name] = is_healthy
                if not is_healthy:
                    overall_status = "degraded"
            except Exception as e:
                logger.error(f"Health check failed for provider {name}: {e}")
                provider_health[name] = False
                overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            providers=provider_health,
            compliance_status={
                "manager_initialized": compliance_manager._request_session is not None
            },
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="error", providers={})


@router.get("/providers", response_model=list[ProviderInfo])
async def get_providers(service=Depends(get_trends_service)):
    """Get information about available providers."""
    providers_info = []

    for name, provider in service.providers.items():
        try:
            info = ProviderInfo(
                name=provider.provider_name,
                supported_regions=provider.supported_regions,
                supported_features=["trending", "hashtag"],
                compliance_level="strict",
            )
            providers_info.append(info)
        except Exception as e:
            logger.warning(f"Failed to get info for provider {name}: {e}")

    return providers_info


@router.get("/compliance", response_model=ComplianceInfo)
async def get_compliance_info():
    """Get compliance information and guidelines."""
    return ComplianceInfo(
        robots_txt_respected=True,
        rate_limiting_enabled=True,
        user_agent=compliance_manager.user_agent,
        supported_protocols=["https"],
        data_retention_policy="No data retention - requests processed in real-time",
    )
