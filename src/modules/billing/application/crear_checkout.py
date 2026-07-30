from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.modules.billing.domain.models import Facturacion, PRECIOS_PLANES, PERIODOS_PLANES
from src.modules.billing.domain.ports import FacturacionRepositoryPort, ConektaPort
from src.modules.billing.domain.exceptions import PlanInvalidoError, CheckoutFallidoError


@dataclass
class CheckoutResult:
    facturacion_id: str
    checkout_url: str
    monto: str
    plan: str
    metodo_pago: str


class CrearCheckout:
    def __init__(
        self,
        facturacion_repo: FacturacionRepositoryPort,
        conekta_port: ConektaPort,
    ):
        self.facturacion_repo = facturacion_repo
        self.conekta_port = conekta_port

    async def execute(self, aseguradora_id: str, plan: str, metodo_pago: str = "all") -> CheckoutResult:
        monto = PRECIOS_PLANES.get(plan)
        if monto is None:
            raise PlanInvalidoError(plan)

        dias = PERIODOS_PLANES.get(plan, 30)
        now = datetime.now(timezone.utc)
        facturacion_id = str(uuid4())

        facturacion = Facturacion(
            id=facturacion_id,
            aseguradora_id=aseguradora_id,
            plan_suscripcion=plan,
            monto=monto,
            moneda="MXN",
            periodo_inicio=now,
            periodo_fin=now + timedelta(days=dias),
            fecha_expiracion=now + timedelta(days=dias),
            estatus_pago="Pendiente",
            gateway="conekta",
        )

        await self.facturacion_repo.save(facturacion)

        try:
            checkout = await self.conekta_port.create_checkout(
                aseguradora_id=aseguradora_id,
                plan=plan,
                monto=monto,
                facturacion_id=facturacion_id,
                metodo_pago=metodo_pago,
            )
        except Exception as e:
            raise CheckoutFallidoError(str(e))

        return CheckoutResult(
            facturacion_id=facturacion_id,
            checkout_url=checkout["checkout_url"],
            monto=str(monto),
            plan=plan,
            metodo_pago=metodo_pago,
        )
