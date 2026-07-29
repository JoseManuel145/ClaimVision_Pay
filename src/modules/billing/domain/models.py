from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


@dataclass
class Facturacion:
    id: str | None
    aseguradora_id: str
    plan_suscripcion: str
    monto: Decimal
    moneda: str = "MXN"
    periodo_inicio: datetime | None = None
    periodo_fin: datetime | None = None
    fecha_pago: datetime | None = None
    fecha_expiracion: datetime | None = None
    estatus_pago: str = "Pendiente"
    metodo_pago: str | None = None
    gateway: str = "conekta"
    gateway_transaccion_id: str | None = None
    metadata: dict[str, Any] | None = None
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


PRECIOS_PLANES = {
    "Basic": Decimal("999.00"),
    "Pro": Decimal("2499.00"),
    "Enterprise": Decimal("9999.00"),
}

PERIODOS_PLANES = {
    "Basic": 30,
    "Pro": 30,
    "Enterprise": 30,
}

LIMITES_PLANES = {
    "Basic": 100,
    "Pro": 500,
    "Enterprise": -1,
}
