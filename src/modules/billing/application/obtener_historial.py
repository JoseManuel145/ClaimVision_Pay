from src.modules.billing.domain.ports import FacturacionRepositoryPort


class ObtenerHistorial:
    def __init__(self, facturacion_repo: FacturacionRepositoryPort):
        self.facturacion_repo = facturacion_repo

    async def execute(
        self, aseguradora_id: str, page: int = 1, limit: int = 20
    ) -> dict:
        offset = (page - 1) * limit
        registros, total = await self.facturacion_repo.list_by_aseguradora(
            aseguradora_id, offset=offset, limit=limit
        )
        return {
            "data": [
                {
                    "id": r.id,
                    "plan_suscripcion": r.plan_suscripcion,
                    "monto": str(r.monto),
                    "moneda": r.moneda,
                    "periodo_inicio": r.periodo_inicio.isoformat() if r.periodo_inicio else None,
                    "periodo_fin": r.periodo_fin.isoformat() if r.periodo_fin else None,
                    "fecha_pago": r.fecha_pago.isoformat() if r.fecha_pago else None,
                    "fecha_expiracion": r.fecha_expiracion.isoformat() if r.fecha_expiracion else None,
                    "estatus_pago": r.estatus_pago,
                    "metodo_pago": r.metodo_pago,
                    "gateway": r.gateway,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in registros
            ],
            "total": total,
            "page": page,
            "limit": limit,
        }
