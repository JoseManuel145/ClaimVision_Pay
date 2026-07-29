from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.modules.billing.application.crear_checkout import CrearCheckout
from src.modules.billing.application.procesar_webhook import ProcesarWebhook
from src.modules.billing.application.obtener_historial import ObtenerHistorial
from src.modules.billing.infra.db.repositories.repositorio_facturacion import RepositorioFacturacion
from src.modules.billing.infra.gateway.adaptador_conekta import AdaptadorConekta


def crear_checkout_service(session: AsyncSession) -> CrearCheckout:
    repo = RepositorioFacturacion(session)
    conekta = AdaptadorConekta()
    return CrearCheckout(repo, conekta)


def procesar_webhook_service(session: AsyncSession) -> ProcesarWebhook:
    repo = RepositorioFacturacion(session)
    conekta = AdaptadorConekta()
    return ProcesarWebhook(repo, conekta)


def obtener_historial_service(session: AsyncSession) -> ObtenerHistorial:
    repo = RepositorioFacturacion(session)
    return ObtenerHistorial(repo)
