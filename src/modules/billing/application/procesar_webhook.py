from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from src.modules.billing.domain.models import LIMITES_PLANES
from src.modules.billing.domain.ports import FacturacionRepositoryPort, ConektaPort
from src.modules.billing.domain.exceptions import FacturacionNoEncontradaError


@dataclass
class WebhookResult:
    status: str
    evento: Optional[str] = None
    aseguradora_id: Optional[str] = None
    plan: Optional[str] = None
    limite_peritajes_mes: Optional[int] = None
    reason: Optional[str] = None


class ProcesarWebhook:
    def __init__(
        self,
        facturacion_repo: FacturacionRepositoryPort,
        conekta_port: ConektaPort,
    ):
        self.facturacion_repo = facturacion_repo
        self.conekta_port = conekta_port

    async def execute(self, payload: dict[str, Any]) -> WebhookResult:
        evento = await self.conekta_port.procesar_evento(payload)

        if evento["evento"] == "pago_completado":
            facturacion_id = evento.get("facturacion_id")
            if not facturacion_id:
                return WebhookResult(status="ignored", reason="sin facturacion_id")

            facturacion = await self.facturacion_repo.get_by_id(facturacion_id)
            if not facturacion:
                raise FacturacionNoEncontradaError(facturacion_id)

            facturacion.estatus_pago = "Completado"
            facturacion.fecha_pago = datetime.now(timezone.utc)
            facturacion.gateway_transaccion_id = evento.get("gateway_transaccion_id")
            facturacion.metodo_pago = evento.get("metodo_pago")
            await self.facturacion_repo.update(facturacion)

            return WebhookResult(
                status="ok",
                evento="pago_completado",
                aseguradora_id=facturacion.aseguradora_id,
                plan=facturacion.plan_suscripcion,
                limite_peritajes_mes=LIMITES_PLANES.get(
                    facturacion.plan_suscripcion, 100
                ),
            )

        if evento["evento"] == "pago_fallido":
            facturacion_id = evento.get("facturacion_id")
            if facturacion_id:
                facturacion = await self.facturacion_repo.get_by_id(facturacion_id)
                if facturacion:
                    facturacion.estatus_pago = "Fallido"
                    await self.facturacion_repo.update(facturacion)

            return WebhookResult(status="ok", evento="pago_fallido")

        return WebhookResult(status="ignored", evento=evento.get("tipo"))
