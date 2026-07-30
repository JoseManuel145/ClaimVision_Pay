from dataclasses import dataclass, field
from src.modules.billing.domain.models import Facturacion
from src.modules.billing.domain.ports import FacturacionRepositoryPort


@dataclass
class HistorialResult:
    data: list[Facturacion]
    total: int
    page: int = 1
    limit: int = 20


class ObtenerHistorial:
    def __init__(self, facturacion_repo: FacturacionRepositoryPort):
        self.facturacion_repo = facturacion_repo

    async def execute(
        self, aseguradora_id: str, page: int = 1, limit: int = 20
    ) -> HistorialResult:
        offset = (page - 1) * limit
        registros, total = await self.facturacion_repo.list_by_aseguradora(
            aseguradora_id, offset=offset, limit=limit
        )
        return HistorialResult(
            data=registros,
            total=total,
            page=page,
            limit=limit,
        )
