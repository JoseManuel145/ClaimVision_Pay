from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from src.modules.billing.domain.models import Facturacion


class FacturacionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, facturacion: Facturacion) -> Facturacion: ...

    @abstractmethod
    async def get_by_id(self, id: str) -> Facturacion | None: ...

    @abstractmethod
    async def list_by_aseguradora(
        self, aseguradora_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[Facturacion], int]: ...

    @abstractmethod
    async def update(self, facturacion: Facturacion) -> Facturacion: ...


class ConektaPort(ABC):
    @abstractmethod
    async def create_checkout(
        self, aseguradora_id: str, plan: str, monto: Decimal, facturacion_id: str
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def procesar_evento(self, payload: dict[str, Any]) -> dict[str, Any]: ...
