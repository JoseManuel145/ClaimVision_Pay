# ClaimVision_Pay

Microservicio de facturación y pagos para ClaimVision. Procesa suscripciones de aseguradoras (Basic/Pro/Enterprise) mediante Conekta.

## Arquitectura

```
ClaimVisionWeb → ClaimVision_Proxy → ClaimVision_Backend (pagos_bridge) → ClaimVision_Pay
```

El Backend actúa como bridge/proxy (mismo patrón que `ia_bridge` con `IAService`). El frontend nunca habla directamente con Pay.

## Estructura del proyecto

```
src/
├── core/
│   ├── config.py              # Pydantic Settings (DB, Conekta keys)
│   ├── database.py            # Async SQLAlchemy engine + session
│   └── exceptions.py          # Global exception handlers
├── modules/billing/
│   ├── domain/
│   │   ├── models.py          # Facturacion (dataclass pura)
│   │   ├── ports.py           # FacturacionRepositoryPort, ConektaPort (ABC)
│   │   └── exceptions.py      # Excepciones de negocio
│   ├── application/
│   │   ├── crear_checkout.py       # Crea checkout en Conekta + registro pendiente
│   │   ├── procesar_webhook.py     # Procesa charge.paid / charge.failed
│   │   ├── obtener_historial.py    # Lista pagos por aseguradora
│   │   └── verificar_renovaciones.py  # (esqueleto para tarea programada)
│   ├── infra/
│   │   ├── db/
│   │   │   ├── tables/tabla_facturacion.py        # SQLAlchemy model
│   │   │   └── repositories/repositorio_facturacion.py  # Implementación del port
│   │   └── gateway/adaptador_conekta.py           # httpx → Conekta API
│   └── presentation/
│       ├── schemas.py          # DTOs segregados (Pydantic V2)
│       ├── dependencies.py     # Fábricas DI
│       └── routes.py           # Endpoints FastAPI
└── main.py
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/pay/checkout` | Crea checkout en Conekta + registro pendiente |
| `POST` | `/api/v1/pay/webhook` | Webhook de Conekta (charge.paid, charge.failed) |
| `GET`  | `/api/v1/pay/historial/{aseguradora_id}` | Historial de pagos de una aseguradora |
| `GET`  | `/health` | Health check |

## Flujo de pago

```
1. Admin (Web) → POST /api/v1/pagos/checkout
   ──▶ Proxy ──▶ Backend (pagos_bridge)
                      │ httpx
                      ▼
                 POST /api/v1/pay/checkout
                      │
                      ├── Crea historial_facturacion (estatus: Pendiente)
                      ├── Crea Order/Checkout en Conekta API
                      └── Devuelve { checkout_url }

2. Usuario paga en Conekta Checkout (tarjeta/OXXO/SPEI)

3. Conekta → POST /api/v1/pagos/webhook
   ──▶ Proxy ──▶ Backend (pagos_bridge)
                      │ httpx
                      ▼
                 POST /api/v1/pay/webhook
                      │
                      ├── Actualiza historial_facturacion → Completado
                      └── Devuelve { aseguradora_id, plan, limite_peritajes_mes }
```

## Precios

| Plan | Precio | Límite de peritajes/mes |
|------|--------|------------------------|
| Basic | $999.00 MXN | 100 |
| Pro | $2,499.00 MXN | 500 |
| Enterprise | $9,999.00 MXN | Ilimitado (-1) |

## Variables de entorno

```env
DATABASE_URL="postgresql+asyncpg://..."
CONEKTA_API_KEY="key_..."
CONEKTA_PUBLIC_KEY="key_..."
CONEKTA_WEBHOOK_SECRET="..."
LOG_LEVEL="DEBUG"
ENVIRONMENT="development"
```

## Base de datos

Requiere en Supabase:

```sql
CREATE TYPE estatus_pago AS ENUM (
  'Pendiente', 'Completado', 'Fallido', 'Reembolsado', 'Expirado'
);

CREATE TABLE historial_facturacion (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  aseguradora_id uuid NOT NULL REFERENCES aseguradoras(id),
  plan_suscripcion text NOT NULL,
  monto numeric(10,2) NOT NULL,
  moneda text NOT NULL DEFAULT 'MXN',
  periodo_inicio timestamptz NOT NULL,
  periodo_fin timestamptz NOT NULL,
  fecha_pago timestamptz,
  fecha_expiracion timestamptz NOT NULL,
  estatus_pago estatus_pago NOT NULL DEFAULT 'Pendiente',
  metodo_pago text,
  gateway text NOT NULL DEFAULT 'conekta',
  gateway_transaccion_id text,
  metadata jsonb,
  version int NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  deleted_at timestamptz
);

CREATE INDEX idx_historial_facturacion_aseguradora
  ON historial_facturacion (aseguradora_id, created_at DESC);
```

## Archivos modificados en otros proyectos

| Archivo | Cambio |
|---------|--------|
| `ClaimVision_Backend/.env` | Se agregó `PAGO_SERVICE_URL` |
| `ClaimVision_Backend/src/core/config.py` | Se agregó `PAGO_SERVICE_URL: str` |
| `ClaimVision_Backend/src/core/routers.py` | Se montó `pagos_router` en `/v1/pagos` |
| `docker-compose.yml` | Se agregó servicio `pay` y `PAGO_SERVICE_URL` en backend |
