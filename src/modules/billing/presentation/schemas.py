from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CheckoutCreateDTO(BaseModel):
    aseguradora_id: str
    plan_suscripcion: str
    metodo_pago: str = "all"


class CheckoutResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    facturacion_id: str
    checkout_url: str
    monto: str
    plan: str
    metodo_pago: str


class FacturacionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_suscripcion: str
    monto: Decimal
    moneda: str
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    fecha_pago: Optional[datetime] = None
    fecha_expiracion: Optional[datetime] = None
    estatus_pago: str
    metodo_pago: Optional[str] = None
    gateway: str
    gateway_transaccion_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HistorialItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_suscripcion: str
    monto: str
    moneda: str
    periodo_inicio: Optional[str] = None
    periodo_fin: Optional[str] = None
    fecha_pago: Optional[str] = None
    fecha_expiracion: Optional[str] = None
    estatus_pago: str
    metodo_pago: Optional[str] = None
    gateway: str
    created_at: Optional[str] = None


class HistorialResponseDTO(BaseModel):
    data: list[HistorialItemDTO]
    total: int
    page: int
    limit: int


class WebhookResponseDTO(BaseModel):
    status: str
    evento: Optional[str] = None
    aseguradora_id: Optional[str] = None
    plan: Optional[str] = None
    limite_peritajes_mes: Optional[int] = None
    reason: Optional[str] = None
