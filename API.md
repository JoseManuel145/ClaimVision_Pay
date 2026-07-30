# ClaimVision Pay — API

## Base URL

```
https://api.actividades.icu/api/v1/pay
```

Gateway: `https://api.actividades.icu/pay/{path}` → proxea a `http://pay:8000/api/v1/pay/{path}`.

---

## Endpoints

### `POST /checkout`

Crea un link de pago en Conekta y registra la facturación pendiente.

**Request body**

| Campo | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `aseguradora_id` | `string` (UUID) | sí | — | ID de la aseguradora |
| `plan_suscripcion` | `string` | sí | — | `Basic`, `Pro` o `Enterprise` |
| `metodo_pago` | `string` | no | `"all"` | Método(s) a mostrar: `"card"`, `"cash"`, `"bank_transfer"` o `"all"` |

**Response `200`**

```json
{
  "facturacion_id": "uuid",
  "checkout_url": "https://pay.conekta.com/link/...",
  "monto": "9999.00",
  "plan": "Enterprise",
  "metodo_pago": "card"
}
```

**Errores**

| Código | Causa |
|---|---|
| `400` | Plan inválido |
| `502` | Error al crear checkout en Conekta |

**Ejemplo curl**

```bash
curl -X POST https://api.actividades.icu/api/v1/pay/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "aseguradora_id": "3821111f-9eea-4911-acc1-81b1c117bf13",
    "plan_suscripcion": "Enterprise",
    "metodo_pago": "card"
  }'
```

---

### `POST /webhook`

Procesa eventos de Conekta (pago completado, declinado, etc.).

**Request body**

Payload genérico de webhook de Conekta. Eventos soportados:

| Evento | Acción |
|---|---|
| `charge.paid` | Marca facturación como Completado, actualiza `gateway_transaccion_id` y `metodo_pago` |
| `charge.declined` | Marca facturación como Fallido |

**Response `200`**

```json
{
  "status": "ok",
  "evento": "pago_completado",
  "aseguradora_id": "uuid",
  "plan": "Enterprise",
  "limite_peritajes_mes": -1,
  "reason": null
}
```

**Ejemplo curl**

```bash
curl -X POST https://api.actividades.icu/api/v1/pay/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "charge.paid",
    "data": {
      "object": {
        "id": "txn_123",
        "metadata": {
          "facturacion_id": "uuid",
          "aseguradora_id": "uuid",
          "plan": "Enterprise"
        }
      }
    }
  }'
```

---

### `GET /historial/{aseguradora_id}`

Obtiene el historial de facturación de una aseguradora.

**Parámetros query**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `page` | `int` | `1` | Número de página (≥ 1) |
| `limit` | `int` | `20` | Resultados por página (1–100) |

**Response `200`**

```json
{
  "data": [
    {
      "id": "uuid",
      "plan_suscripcion": "Enterprise",
      "monto": "9999.00",
      "moneda": "MXN",
      "periodo_inicio": "2026-01-01T00:00:00+00:00",
      "periodo_fin": "2026-01-31T00:00:00+00:00",
      "fecha_pago": null,
      "fecha_expiracion": "2026-01-31T00:00:00+00:00",
      "estatus_pago": "Pendiente",
      "metodo_pago": null,
      "gateway": "conekta",
      "created_at": "2026-01-01T00:00:00+00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

**Ejemplo curl**

```bash
curl -X GET 'https://api.actividades.icu/api/v1/pay/historial/3821111f-9eea-4911-acc1-81b1c117bf13?page=1&limit=20'
```

---

## Planes y precios

| Plan | Precio mensual | Período (días) | Límite peritajes/mes |
|---|---|---|---|
| `Basic` | $999.00 MXN | 30 | 100 |
| `Pro` | $2,499.00 MXN | 30 | 500 |
| `Enterprise` | $9,999.00 MXN | 30 | Ilimitado |

## Webhooks de Conekta

Configurar en el panel de Conekta (`https://panel.conekta.com`) la URL:

```
https://api.actividades.icu/api/v1/pay/webhook
```

Eventos a suscribir:
- `charge.paid`
- `charge.declined`

## Flujo de pago (frontend)

```
1. App → POST /checkout → recibe checkout_url
2. App abre checkout_url en navegador/in-app browser
3. Usuario paga en página de Conekta (card / OXXO / SPEI)
4. Conekta → POST /webhook (charge.paid) → Pay marca facturación como Completado
5. App → GET /historial/{id} → consulta estado del pago
```

> `limite_peritajes_mes` se usa en el backend transaccional para controlar el límite de peritajes de la aseguradora. Se actualiza automáticamente al recibir `charge.paid`.
