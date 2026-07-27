# Planes y Precios — Medicamentum360

**Versión:** 1.0 · **Fecha:** 2026-07-27
**Propósito:** Información completa sobre modelos de precios para agentes de IA y equipo comercial.

---

## 1. Modelo de negocio

Medicamentum360 opera con un modelo **transaccional + comisión**, no por suscripción:

1. **Compra individual de productos:** cada curso, experiencia VR o automatización se paga por separado en el marketplace.
2. **Compra corporativa en lote (B2B):** las organizaciones compran múltiples cupos de un mismo curso para sus empleados.
3. **Marketplace multi-vendor con comisión:** los vendedores externos retienen el 80% del precio de venta; Medicamentum360 cobra 20% de comisión.

No existen planes de suscripción mensual ni anual para acceder a la plataforma. El registro como estudiante/comprador es gratuito.

---

## 2. Precios de productos

### 2.1 ¿Quién define los precios?

| Tipo de producto | Quién define el precio |
|---|---|
| Producto propio de Medicamentum360 | `super_admin` desde el panel de administración |
| Producto de vendor externo | El propio vendor al crear el producto |
| VR Experiences | El administrador (`super_admin`) o vendor |

### 2.2 Moneda y facturación

- **Moneda:** Peso colombiano (COP).
- **IVA:** 19% (configurable vía `DEFAULT_TAX_RATE`).
- **Facturación electrónica:** se solicita NIT o CC durante el checkout. La facturación electrónica completa (DIAN) está planificada para la Fase 13.

### 2.3 Transparencia de precios

- El precio mostrado en el marketplace es el precio final (no hay cargos ocultos).
- El IVA se desglosa en el checkout.
- El precio se muestra consistente en todas partes: tarjeta del marketplace, detalle de producto, carrito y checkout.

---

## 3. Compra individual

### 3.1 Flujo de precios

```
Precio base del producto
  + IVA (19%)
  ─────────────
  = Total a pagar
```

### 3.2 Procesamiento

- Pago único por producto.
- Acceso inmediato al curso tras la confirmación del pago por Wompi.
- Sin suscripción recurrente: pagas una vez, accedes para siempre (o mientras el curso esté disponible en la plataforma).
- **Sin cargos adicionales** por generación de certificados, emisión de factura, o acceso al contenido.

---

## 4. Compra corporativa en lote (B2B)

### 4.1 ¿Quién puede comprar?
Exclusivamente usuarios con rol `hospital_admin` de una organización registrada.

### 4.2 ¿Cómo funciona?
1. En el detalle del producto, el `hospital_admin` activa "Comprar para mi organización".
2. Selecciona cantidad de empleados.
3. Precio total = `precio unitario × cantidad + IVA`.
4. Pago único vía Wompi (mismo flujo que compra individual).
5. Tras el pago, los cupos quedan disponibles para asignar a empleados desde `/org/employees`.

### 4.3 Precios por volumen
Actualmente **no hay descuento automático por volumen**. El precio por cupo es el mismo independientemente de la cantidad comprada. Descuentos por volumen están anotados como mejora futura (ver `TRD.md §22`).

### 4.4 Cupos no asignados
Los cupos comprados pero no asignados **no caducan** en la fase actual. Una política de expiración (ej. 1 año) está en evaluación para fases posteriores.

---

## 5. Marketplace Multi-Vendor — Comisión

### 5.1 Estructura de comisión

| Concepto | Valor |
|---|---|
| **Comisión estándar** | 20% del precio de venta |
| **El vendor recibe** | 80% del precio de venta |
| **Comisión negociada** | Configurable por vendor (`Vendor.commissionPct`, mínimo desde `MARKETPLACE_COMMISSION_PCT`) |

### 5.2 Ejemplo de liquidación

```
Venta de un curso:                    $100,000 COP
Comisión Medicamentum360 (20%):      -$20,000 COP
Neto para el vendor:                  $80,000 COP
```

### 5.3 Payout (pago al vendor)

- **Frecuencia:** mensual.
- **Cálculo:** suma de ventas netas del mes (después de descontar comisión).
- **Revisión:** el lote mensual es revisado y aprobado manualmente por `super_admin` antes de ejecutar el pago.
- **Método de pago:** transferencia bancaria vía Wompi.
- **Monto mínimo de payout:** sin mínimo en la fase actual (toda venta genera payout, por pequeña que sea).

### 5.4 El comprador no ve diferencia

El precio que ve el comprador en el marketplace es el mismo, independientemente de si el producto es de Medicamentum360 o de un vendor externo. La comisión es un acuerdo entre Medicamentum360 y el vendor, transparente para el estudiante.

### 5.5 Vendor suspendido
Si un vendor es suspendido, las ventas ya realizadas antes de la suspensión generan payout normalmente. Los payouts pendientes de periodos anteriores también se procesan. La suspensión solo afecta ventas futuras (sus productos se despublican).

---

## 6. Reembolsos

### 6.1 Política de reembolso

| Condición | Detalle |
|---|---|
| **Ventana de tiempo** | 7 días desde la fecha de compra |
| **Progreso máximo** | Menos del 20% del curso completado |
| **Experiencias VR** | 7 días desde la compra (si el código no fue redimido) |

### 6.2 Costo del reembolso
El reembolso es por el monto total de la compra. Medicamentum360 no cobra cargos por procesar reembolsos. El monto se reversa vía Wompi.

### 6.3 Reembolso de compras corporativas
El reembolso aplica a la orden completa. No hay reembolso parcial de cupos individuales en la fase actual. Si una organización necesita reembolso solo de cupos sin asignar, debe contactar a soporte.

---

## 7. Costos operativos (internos, no visibles al usuario)

Estos son los costos que Medicamentum360 asume por infraestructura:

| Servicio | Costo estimado mensual |
|---|---|
| **VPS** (Hetzner CX22: 2 vCPU, 4 GB RAM) | ~$25,000 COP (€5.77) |
| **Cloudflare R2** (almacenamiento) | ~$0 COP (free tier: 10 GB) |
| **Cloudflare Stream** (video) | ~$5 USD por 1,000 minutos almacenados + ~$1 USD por 1,000 minutos entregados |
| **Brevo** (email transaccional) | ~$0 COP (free tier: 300 emails/día) |
| **Sentry** (error tracking) | ~$0 COP (free tier: 5,000 errores/mes) |
| **UptimeRobot** (monitoreo) | Gratuito |
| **Dominio + SSL** | ~$50,000 COP/año (dominio .com) + Let's Encrypt gratis |

---

## 8. Impuestos y cumplimiento fiscal

- **IVA:** 19% sobre productos digitales en Colombia.
- **Facturación:** se recopilan NIT o CC para facturación electrónica (Fase 13 — DIAN).
- **Retención en la fuente para vendors:** a definir según la normativa colombiana aplicable a pagos a proveedores/contratistas. La plataforma calcula la comisión pero no retiene impuestos automáticamente en la fase actual (responsabilidad del vendor declarar sus ingresos).

---

## 9. Medios de pago aceptados

A través de **Wompi**:
- Tarjetas de crédito: Visa, Mastercard, American Express
- Tarjetas débito
- PSE (Pagos Seguros en Línea — transferencia desde bancos colombianos)
- Nequi
- Daviplata

---

## 10. Preguntas frecuentes sobre precios

**P: ¿Hay planes de suscripción?**
R: No. El modelo actual es pago por producto. Cada curso o experiencia se compra individualmente.

**P: ¿Puedo pagar en cuotas?**
R: Depende de lo que ofrezca Wompi y tu banco emisor. La plataforma no gestiona cuotas directamente.

**P: ¿Emiten factura electrónica?**
R: La emisión completa de factura electrónica DIAN está planificada para la Fase 13. Actualmente se emite un comprobante de compra con los datos fiscales.

**P: Si soy vendor, ¿cuándo recibo mi primer pago?**
R: Los payouts se procesan mensualmente. Si tuviste ventas en un mes, recibirás tu pago al mes siguiente, tras la revisión del lote por parte del equipo.

**P: ¿Hay un mínimo de ventas para recibir payout?**
R: No en la fase actual. Todas las ventas del periodo generan payout, sin importar el monto.

**P: ¿Los precios incluyen IVA?**
R: El precio mostrado es el precio base. El IVA (19%) se calcula y se muestra en el checkout.
