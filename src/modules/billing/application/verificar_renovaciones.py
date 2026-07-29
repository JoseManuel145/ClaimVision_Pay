from datetime import datetime, timezone

from src.modules.billing.domain.ports import FacturacionRepositoryPort, ConektaPort


class VerificarRenovaciones:
    def __init__(
        self,
        facturacion_repo: FacturacionRepositoryPort,
        conekta_port: ConektaPort,
    ):
        self.facturacion_repo = facturacion_repo
        self.conekta_port = conekta_port

    async def execute(self) -> dict:
        now = datetime.now(timezone.utc)
        renovaciones = []
        return {"message": "funcionalidad no implementada", "renovaciones": renovaciones}
