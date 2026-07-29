class PlanInvalidoError(Exception):
    def __init__(self, plan: str):
        self.plan = plan
        super().__init__(f"Plan '{plan}' no válido")


class FacturacionNoEncontradaError(Exception):
    def __init__(self, facturacion_id: str):
        self.facturacion_id = facturacion_id
        super().__init__(f"Facturación {facturacion_id} no encontrada")


class CheckoutFallidoError(Exception):
    def __init__(self, detalle: str):
        self.detalle = detalle
        super().__init__(f"Error al crear checkout: {detalle}")


class WebhookInvalidoError(Exception):
    def __init__(self, evento: str):
        self.evento = evento
        super().__init__(f"Webhook ignorado: evento '{evento}' no reconocido")
