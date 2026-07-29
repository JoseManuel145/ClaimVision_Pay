from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.models import Facturacion
from src.modules.billing.domain.ports import FacturacionRepositoryPort
from src.modules.billing.domain.exceptions import FacturacionNoEncontradaError
from src.modules.billing.infra.db.tables.tabla_facturacion import FacturacionTable


class RepositorioFacturacion(FacturacionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, facturacion: Facturacion) -> Facturacion:
        now = datetime.now(timezone.utc)
        record = FacturacionTable(
            id=uuid4() if facturacion.id is None else facturacion.id,
            aseguradora_id=facturacion.aseguradora_id,
            plan_suscripcion=facturacion.plan_suscripcion,
            monto=facturacion.monto,
            moneda=facturacion.moneda,
            periodo_inicio=facturacion.periodo_inicio or now,
            periodo_fin=facturacion.periodo_fin or now,
            fecha_pago=facturacion.fecha_pago,
            fecha_expiracion=facturacion.fecha_expiracion or now,
            estatus_pago=facturacion.estatus_pago,
            metodo_pago=facturacion.metodo_pago,
            gateway=facturacion.gateway,
            gateway_transaccion_id=facturacion.gateway_transaccion_id,
            metadata=facturacion.metadata,
            version=1,
            created_at=now,
            updated_at=now,
        )
        self.session.add(record)
        await self.session.flush()
        return self._to_domain(record)

    async def get_by_id(self, id: str) -> Facturacion | None:
        stmt = select(FacturacionTable).where(FacturacionTable.id == id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return self._to_domain(record) if record else None

    async def list_by_aseguradora(
        self, aseguradora_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[Facturacion], int]:
        count_stmt = select(func.count()).where(
            FacturacionTable.aseguradora_id == aseguradora_id,
            FacturacionTable.deleted_at.is_(None),
        )
        total = (await self.session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(FacturacionTable)
            .where(
                FacturacionTable.aseguradora_id == aseguradora_id,
                FacturacionTable.deleted_at.is_(None),
            )
            .offset(offset)
            .limit(limit)
            .order_by(FacturacionTable.created_at.desc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [self._to_domain(r) for r in records], total

    async def update(self, facturacion: Facturacion) -> Facturacion:
        stmt = select(FacturacionTable).where(FacturacionTable.id == facturacion.id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            raise FacturacionNoEncontradaError(facturacion.id)

        record.plan_suscripcion = facturacion.plan_suscripcion
        record.monto = facturacion.monto
        record.fecha_pago = facturacion.fecha_pago
        record.fecha_expiracion = facturacion.fecha_expiracion
        record.estatus_pago = facturacion.estatus_pago
        record.metodo_pago = facturacion.metodo_pago
        record.gateway_transaccion_id = facturacion.gateway_transaccion_id
        record.metadata = facturacion.metadata
        record.updated_at = datetime.now(timezone.utc)
        record.version += 1

        await self.session.flush()
        return self._to_domain(record)

    def _to_domain(self, record: FacturacionTable) -> Facturacion:
        return Facturacion(
            id=str(record.id),
            aseguradora_id=str(record.aseguradora_id),
            plan_suscripcion=record.plan_suscripcion,
            monto=record.monto,
            moneda=record.moneda,
            periodo_inicio=record.periodo_inicio,
            periodo_fin=record.periodo_fin,
            fecha_pago=record.fecha_pago,
            fecha_expiracion=record.fecha_expiracion,
            estatus_pago=record.estatus_pago,
            metodo_pago=record.metodo_pago,
            gateway=record.gateway,
            gateway_transaccion_id=record.gateway_transaccion_id,
            metadata=record.metadata,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            deleted_at=record.deleted_at,
        )
