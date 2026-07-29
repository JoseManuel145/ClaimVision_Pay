from datetime import datetime, timezone
from typing import Any

from src.modules.billing.domain.models import LIMITES_PLANES
from src.modules.billing.domain.ports import FacturacionRepositoryPort, ConektaPort
from src.modules.billing.domain.exceptions import FacturacionNoEncontradaError


class ProcesarWebhook:
    def __init__(
        self,
        facturacion_repo: FacturacionRepositoryPort,
        conekta_port: ConektaPort,
    ):
        self.facturacion_repo = facturacion_repo
        self.conekta_port = conekta_port

    async def execute(self, payload: dict[str, Any]) -> dict:
        evento = await self.conekta_port.procesar_evento(payload)

        if evento["evento"] == "pago_completado":
            facturacion_id = evento.get("facturacion_id")
            if not facturacion_id:
                return {"status": "ignored", "reason": "sin facturacion_id"}

            facturacion = await self.facturacion_repo.get_by_id(facturacion_id)
            if not facturacion:
                raise FacturacionNoEncontradaError(facturacion_id)

            facturacion.estatus_pago = "Completado"
            facturacion.fecha_pago = datetime.now(timezone.utc)
            facturacion.gateway_transaccion_id = evento.get("gateway_transaccion_id")
            facturacion.metodo_pago = evento.get("metodo_pago")
            await self.facturacion_repo.update(facturacion)

            return {
                "status": "ok",
                "evento": "pago_completado",
                "aseguradora_id": facturacion.aseguradora_id,
                "plan": facturacion.plan_suscripcion,
                "limite_peritajes_mes": LIMITES_PLANES.get(
                    facturacion.plan_suscripcion, 100
                ),
            }

        if evento["evento"] == "pago_fallido":
            facturacion_id = evento.get("facturacion_id")
            if facturacion_id:
                facturacion = await self.facturacion_repo.get_by_id(facturacion_id)
                if facturacion:
                    facturacion.estatus_pago = "Fallido"
                    await self.facturacion_repo.update(facturacion)

            return {"status": "ok", "evento": "pago_fallido"}

        return {"status": "ignored", "evento": evento.get("tipo")}
