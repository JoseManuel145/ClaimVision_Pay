from sqlalchemy import Column, String, DateTime, Enum, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.core.database import Base
import enum


class EstatusPago(str, enum.Enum):
    PENDIENTE = "Pendiente"
    COMPLETADO = "Completado"
    FALLIDO = "Fallido"
    REEMBOLSADO = "Reembolsado"
    EXPIRADO = "Expirado"


class FacturacionTable(Base):
    __tablename__ = "historial_facturacion"

    id = Column(UUID(as_uuid=True), primary_key=True)
    aseguradora_id = Column(UUID(as_uuid=True), nullable=False)
    plan_suscripcion = Column(String, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String, nullable=False, default="MXN")
    periodo_inicio = Column(DateTime(timezone=True), nullable=False)
    periodo_fin = Column(DateTime(timezone=True), nullable=False)
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    estatus_pago = Column(
        Enum(EstatusPago, name="estatus_pago", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EstatusPago.PENDIENTE.value,
    )
    metodo_pago = Column(String, nullable=True)
    gateway = Column(String, nullable=False, default="conekta")
    gateway_transaccion_id = Column(String, nullable=True)
    datos_adicionales = Column("metadata", JSONB, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
