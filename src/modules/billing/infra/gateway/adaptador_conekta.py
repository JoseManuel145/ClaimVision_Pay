from decimal import Decimal
from typing import Any

import httpx

from src.core.config import settings


class AdaptadorConekta:
    BASE_URL = "https://api.conekta.io"

    def __init__(self):
        self.api_key = settings.CONEKTA_API_KEY
        self.public_key = settings.CONEKTA_PUBLIC_KEY

    async def create_checkout(
        self, aseguradora_id: str, plan: str, monto: Decimal, facturacion_id: str
    ) -> dict[str, Any]:
        centavos = int(monto * 100)
        payload = {
            "name": f"Plan {plan} - ClaimVision",
            "type": "Subscription",
            "recurrent": False,
            "amount": centavos,
            "currency": "MXN",
            "metadata": {
                "aseguradora_id": aseguradora_id,
                "facturacion_id": facturacion_id,
                "plan": plan,
            },
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/checkouts",
                json=payload,
                headers={
                    "Authorization": f"Basic {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "checkout_url": data.get("url"),
                "id": data.get("id"),
                "status": data.get("status"),
            }

    async def procesar_evento(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_type = payload.get("type", "")
        data = payload.get("data", {}).get("object", {})

        if event_type == "charge.paid":
            metadata = data.get("metadata", {})
            return {
                "evento": "pago_completado",
                "gateway_transaccion_id": data.get("id"),
                "facturacion_id": metadata.get("facturacion_id"),
                "aseguradora_id": metadata.get("aseguradora_id"),
                "plan": metadata.get("plan"),
                "metodo_pago": data.get("payment_method", {}).get("type"),
            }

        if event_type == "charge.declined":
            metadata = data.get("metadata", {})
            return {
                "evento": "pago_fallido",
                "gateway_transaccion_id": data.get("id"),
                "facturacion_id": metadata.get("facturacion_id"),
                "error": data.get("failure_message"),
            }

        return {"evento": "ignorado", "tipo": event_type}
