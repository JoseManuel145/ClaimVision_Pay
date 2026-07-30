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
from src.modules.billing.application.crear_checkout import CheckoutResult
from src.modules.billing.application.procesar_webhook import WebhookResult
from src.modules.billing.application.obtener_historial import HistorialResult
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
        resultado: CheckoutResult = await uc.execute(
            aseguradora_id=body.aseguradora_id,
            plan=body.plan_suscripcion,
            metodo_pago=body.metodo_pago,
        )
        return CheckoutResponseDTO(
            facturacion_id=resultado.facturacion_id,
            checkout_url=resultado.checkout_url,
            monto=resultado.monto,
            plan=resultado.plan,
            metodo_pago=resultado.metodo_pago,
        )
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
        resultado: WebhookResult = await uc.execute(payload)
        return WebhookResponseDTO(
            status=resultado.status,
            evento=resultado.evento,
            aseguradora_id=resultado.aseguradora_id,
            plan=resultado.plan,
            limite_peritajes_mes=resultado.limite_peritajes_mes,
            reason=resultado.reason,
        )
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
    resultado: HistorialResult = await uc.execute(aseguradora_id, page=page, limit=limit)
    return HistorialResponseDTO(
        data=[
            HistorialItemDTO(
                id=r.id,
                plan_suscripcion=r.plan_suscripcion,
                monto=str(r.monto),
                moneda=r.moneda,
                periodo_inicio=r.periodo_inicio.isoformat() if r.periodo_inicio else None,
                periodo_fin=r.periodo_fin.isoformat() if r.periodo_fin else None,
                fecha_pago=r.fecha_pago.isoformat() if r.fecha_pago else None,
                fecha_expiracion=r.fecha_expiracion.isoformat() if r.fecha_expiracion else None,
                estatus_pago=r.estatus_pago,
                metodo_pago=r.metodo_pago,
                gateway=r.gateway,
                created_at=r.created_at.isoformat() if r.created_at else None,
            )
            for r in resultado.data
        ],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
