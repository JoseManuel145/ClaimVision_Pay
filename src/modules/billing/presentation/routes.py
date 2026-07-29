from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.modules.billing.domain.exceptions import (
    PlanInvalidoError,
    FacturacionNoEncontradaError,
    CheckoutFallidoError,
)
from src.modules.billing.presentation.schemas import (
    CheckoutCreateDTO,
    CheckoutResponseDTO,
    HistorialResponseDTO,
    WebhookResponseDTO,
)
from src.modules.billing.presentation.dependencies import (
    crear_checkout_service,
    procesar_webhook_service,
    obtener_historial_service,
)

router = APIRouter()


@router.post("/checkout", response_model=CheckoutResponseDTO)
async def crear_checkout(
    body: CheckoutCreateDTO,
    session: AsyncSession = Depends(get_session),
):
    uc = crear_checkout_service(session)
    try:
        resultado = await uc.execute(
            aseguradora_id=body.aseguradora_id,
            plan=body.plan_suscripcion,
        )
        return resultado
    except PlanInvalidoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CheckoutFallidoError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post("/webhook", response_model=WebhookResponseDTO)
async def webhook(
    payload: dict,
    session: AsyncSession = Depends(get_session),
):
    uc = procesar_webhook_service(session)
    try:
        return await uc.execute(payload)
    except FacturacionNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/historial/{aseguradora_id}", response_model=HistorialResponseDTO)
async def obtener_historial(
    aseguradora_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    uc = obtener_historial_service(session)
    return await uc.execute(aseguradora_id, page=page, limit=limit)
