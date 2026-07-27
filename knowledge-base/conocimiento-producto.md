# Base de Conocimiento de Medicamentum360

**Versión:** 1.0 · **Fecha:** 2026-07-27
**Propósito:** Fuente de verdad para agentes de IA que responden preguntas sobre el producto.

---

## 1. ¿Qué es Medicamentum360?

Medicamentum360 es una plataforma SaaS de e-learning y marketplace para el sector salud en Colombia. Permite a hospitales, clínicas y profesionales de la salud comprar, crear y vender cursos médicos, experiencias de realidad virtual (VR) y automatizaciones clínicas.

### Propuesta de valor
- **Marketplace centralizado** de formación médica para profesionales de la salud en Colombia.
- **Course Builder propio** que permite a instructores y estudios VR crear cursos completos (módulos, lecciones, video, quizzes, certificación) sin depender de herramientas externas.
- **Marketplace multi-vendor:** la plataforma se abre a instructores externos y estudios de VR que quieren vender sus propios cursos, con comisión y payout.
- **Capacitación corporativa (B2B):** hospitales y clínicas compran cupos en lote para sus empleados, gestionan quién tiene acceso y monitorean el progreso de cumplimiento.
- **Integración con Moodle** como LMS complementario para cursos legacy, con creación automática de shell de curso y SSO.

---

## 2. Arquitectura general

```
Medicamentum360 (Next.js App Router, Docker standalone)
    │
    ├── Nginx (SSL, proxy inverso, rate limiting)
    │
    ├── Postgres 16 (Docker en VPS propio)
    ├── Redis 7 (caché, rate limiting)
    ├── Meilisearch v1.13 (búsqueda del marketplace)
    │
    ├── Cloudflare R2 (storage: imágenes, PDFs, modelos 3D, certificados)
    ├── Cloudflare Stream (video de lecciones — HLS firmado)
    │
    ├── Wompi (pasarela de pagos para Colombia)
    ├── Brevo (email transaccional)
    ├── Better Auth (autenticación: email+password + Google OAuth)
    └── Moodle (LMS headless en lms.medicamentum360.com)
```

### Stack tecnológico

| Capa | Tecnología |
|---|---|
| Framework | Next.js 15 (App Router, standalone mode) |
| Base de datos | Postgres 16 (Docker en VPS) |
| ORM | Prisma 7 con `@prisma/adapter-pg` |
| Seguridad de datos | Row Level Security (RLS) en Postgres — aislamiento multi-tenant |
| Autenticación | Better Auth 1.6.20 (email+password + Google OAuth) |
| Caché / Rate Limit | Redis 7 |
| Pagos | Wompi (webhook con validación HMAC-SHA256) |
| LMS | Moodle (headless, solo inscripción y SSO) |
| Búsqueda | Meilisearch v1.13 |
| Storage | Cloudflare R2 (compatible S3) |
| Video | Cloudflare Stream (HLS adaptativo, signed URLs) |
| Email | Brevo (transaccional) |
| Reverse proxy | Nginx (SSL, rate limiting, streaming RSC) |
| Contenedores | Docker Compose |
| CI/CD | GitHub Actions (deploy SSH al VPS) |

---

## 3. Roles de usuario

| Rol | Descripción |
|---|---|
| `super_admin` | Administrador general de la plataforma. Puede crear productos, gestionar organizaciones, aprobar/rechazar vendors, revisar reembolsos, generar payouts. |
| `hospital_admin` | Administrador de una organización/hospital. Invita empleados, compra cupos en lote, asigna cursos a empleados, gestiona roles, ve reportes de progreso. |
| `student` | Empleado/estudiante. Puede comprar cursos individuales, consumir lecciones, tomar quizzes, obtener certificados. |
| `vendor` | Instructor o estudio VR externo. Puede registrarse como vendedor, crear cursos/producots, enviarlos a revisión, y recibir pagos por ventas (con comisión). |

Un mismo usuario puede tener múltiples roles que coexisten (ej. `hospital_admin` + `vendor`).

---

## 4. Tipos de productos

| Tipo | Descripción |
|---|---|
| **Curso** | Contenido pedagógico con módulos, lecciones (video/texto/quiz/recurso), drip content, quizzes, y certificado al completar. |
| **Experiencia VR** | Experiencia de realidad virtual accesible mediante código de redención para dispositivos Meta Quest u otros visores. El visor 3D en el detalle es demostrativo. |
| **Automatización** | Herramientas o flujos automatizados para entornos clínicos. |

---

## 5. Marketplace

### 5.1 Descubrimiento de productos
- **Búsqueda:** barra de búsqueda en `/productos`, integrada con Meilisearch (fallback a DB).
- **Filtros por categoría:** Todos / VR / Cursos / Automatizaciones.
- **Ordenamiento:** Más recientes, Precio bajo, Precio alto.
- **Infinite scroll:** 8 productos por página con skeleton loading.
- **Atribución de vendor:** si el producto pertenece a un vendor externo, se muestra "por: {Vendor.displayName}" en la tarjeta.

### 5.2 Detalle de producto
- Carrusel de imágenes o visor 3D (para VR).
- Temario expandible con módulos y lecciones (para cursos `contentSource: native`).
- Lecciones marcadas como "vista previa" (`isPreview: true`) visibles sin comprar.
- Módulos con drip muestran "Se desbloquea tras N días de inscripción".
- Columna derecha sticky con precio, cantidad, botón de compra, garantía/reembolso.

### 5.3 Carrito
- **Popover** (no página ni modal). Ancho 420-480px, alto máx 70vh.
- Persiste en `localStorage` para usuarios no autenticados (guest).
- Merge automático al iniciar sesión (unión de carritos, sin reemplazo).
- Alerta inline si el usuario ya tiene acceso a un producto.
- Móvil: bottom sheet.

---

## 6. Course Builder (creación de cursos)

El Course Builder permite crear cursos completos directamente desde Medicamentum360, sin depender de Moodle.

### 6.1 Estrategia de Moodle
- El shell del curso (nombre, categoría, visibilidad) **sí se crea en Moodle** automáticamente (`core_course_create_courses`) y se vincula vía `Product.moodleCourseId`.
- El contenido pedagógico (módulos, lecciones, video, quizzes) **vive en Postgres** propio, no en Moodle, porque la API REST de Moodle no expone funciones para crear secciones, recursos ni quizzes.
- Para cursos legacy (`contentSource: moodle_legacy`), el contenido sigue viviendo en Moodle y se accede vía SSO.

### 6.2 Estructura de un curso (`contentSource: native`)
```
Curso
  ├── Módulo 1 (orden 0, releaseAfterDays: null)
  │   ├── Lección 1.1 (video, Cloudflare Stream, duración 12:30)
  │   ├── Lección 1.2 (texto, contenido enriquecido)
  │   └── Lección 1.3 (quiz, 5 preguntas opción múltiple)
  ├── Módulo 2 (orden 1, releaseAfterDays: 7 — drip content)
  │   ├── Lección 2.1 (video)
  │   └── Lección 2.2 (recurso descargable PDF)
  └── Módulo 3 (orden 2)
      └── ...
```

### 6.3 Tipos de lección

| Tipo | Descripción |
|---|---|
| `video` | Video alojado en Cloudflare Stream. Subida directa desde el navegador al CDN de Cloudflare. |
| `text` | Contenido enriquecido (Markdown/HTML saneado) con editor WYSIWYG. |
| `quiz` | Evaluación con preguntas de opción única, múltiple o verdadero/falso. |
| `resource` | Archivo descargable (PDF, slides). Se marca como "visto" al abrir. |

### 6.4 Video (Cloudflare Stream)
- El video **nunca** se sirve desde R2. R2 es solo para archivos estáticos.
- Cloudflare Stream transcodifica automáticamente a HLS adaptativo (múltiples calidades).
- Entrega mediante **signed URLs** (tokens RS256 con expiración): el manifiesto y los segmentos solo se sirven con token válido.
- `requireSignedURLs: true` + `allowedOrigins` restringido al dominio de producción.
- El archivo se sube **directo a Cloudflare** (Direct Creator Upload), nunca pasa por el servidor Next.js.
- El token de reproducción se renueva automáticamente antes de expirar.

### 6.5 Quizzes
- Tipos de pregunta: `single_choice`, `multiple_choice`, `true_false`.
- Cada pregunta tiene opciones (mínimo 1 marcada como correcta) y explicación opcional (visible tras responder).
- Configuración por quiz: intentos máximos (ilimitado por defecto), tiempo límite, mezclar preguntas.
- Cálculo de puntuación server-side (nunca en el cliente).
- `passingScorePct` configurable por curso (default 70%).
- Revisión pregunta por pregunta tras enviar.

### 6.6 Validaciones antes de publicar
- Ningún módulo puede estar vacío (sin lecciones).
- Las lecciones de video deben estar en estado "ready" (no "Procesando" ni "Error").
- Cada quiz debe tener al menos 1 pregunta y cada pregunta al menos 1 opción correcta.
- Es obligatoria imagen de portada (advertencia no bloqueante).

---

## 7. Marketplace Multi-Vendor

Hasta la v3.0 todos los productos los creaba el `super_admin`. Desde la Fase 6.5, la plataforma se abre a vendedores externos.

### 7.1 Flujo de onboarding de vendor
1. Usuario se registra en `/vender` completando nombre público, bio y tipo de contenido.
2. Completa KYC: datos fiscales (NIT/CC, certificado bancario) y datos de cuenta bancaria.
3. Los datos bancarios se **cifran a nivel de aplicación** (AES-256-GCM) antes de persistir — nunca visibles en texto plano ni siquiera para `super_admin`.
4. `super_admin` revisa y aprueba el perfil del vendor.
5. Vendor recibe email de bienvenida con acceso al Course Builder (`/instructor`).

### 7.2 Flujo editorial de productos de vendor
1. Vendor crea su producto (curso o VR) en el Course Builder.
2. En vez de "Publicar", usa "Enviar para revisión" → `reviewStatus: pending_review`.
3. `super_admin` revisa el producto completo en `/admin/review-queue` (vista previa real).
4. Puede aprobar (queda disponible para que el vendor lo publique) o rechazar (con motivo obligatorio enviado al vendor).
5. **Ningún producto de vendor llega a `published: true` sin `reviewStatus: approved`.**

### 7.3 Comisión y payouts
- **Comisión por defecto:** 20% (`MARKETPLACE_COMMISSION_PCT`), configurable por vendor.
- **Payout mensual:** un cron job calcula ventas del periodo, descuenta comisión y genera `Payout` en estado `pending`.
- `super_admin` revisa y aprueba manualmente el lote antes de disparar transferencias reales.
- El pago se realiza vía Wompi a la cuenta bancaria del vendor (`WOMPI_VENDOR_PAYOUT_KEY`, credencial separada).
- El vendor ve su historial de payouts (solo lectura) en su panel.
- **Nunca automático en el primer ciclo:** requiere aprobación humana.

### 7.4 Suspensión de vendor
- `super_admin` puede suspender un vendor (`Vendor.status: suspended`).
- Todos sus productos se despublican automáticamente (no se eliminan).
- Los estudiantes con `Enrollment` activo **mantienen su acceso** a contenido ya comprado.
- Payouts pendientes de periodos anteriores se procesan normalmente.

---

## 8. Compra corporativa (B2B)

### 8.1 Modelo de EmployeeAssignment
Un hospital compra cupos de un curso para sus empleados. La compra la paga la organización, pero el acceso se asigna a personas concretas.

### 8.2 Flujo
1. `hospital_admin` activa el toggle "Comprar para mi organización" en el detalle de producto.
2. Selecciona cantidad de empleados (mínimo 1). Precio = `unitario × cantidad`.
3. Checkout normal vía Wompi → `Order` se crea con `organizationId` y `quantity: N`.
4. **No se crea `Enrollment` automático** — los N cupos quedan sin asignar.
5. `hospital_admin` asigna cupos a empleados desde `/org/employees` → se crea `EmployeeAssignment` + `Enrollment`.
6. Cupos no asignados se muestran en banner persistente.
7. Al remover un empleado, el `EmployeeAssignment` se revoca pero el cupo se libera para reasignar.
8. Remover un empleado **no** borra su `Enrollment` ni revoca certificados ya emitidos.

---

## 9. Consumo de cursos por el estudiante

### 9.1 Reproductor de lección
- Layout de 2 columnas: reproductor + sidebar del temario.
- Navegación "Anterior/Siguiente" respetando orden de módulos/lecciones.
- Módulos bloqueados por drip muestran fecha de desbloqueo.
- Estados de lección: ✓ completada, ● actual, · pendiente, 🔒 bloqueada.

### 9.2 Progreso
- **Video:** auto-marcado al 90% de duración.
- **Texto/Recurso:** marcado manualmente por el estudiante.
- **Quiz:** completado al enviar respuestas (aprobado o no).
- `Enrollment.progressPct` se recalcula en tiempo real: `completadas / total × 100`.
- Al 100% y quizzes aprobados → `Enrollment.status = "completed"` → certificado disponible.

### 9.3 Certificados
- PDF generado con jsPDF (diseño branded: nombre, curso, fecha, QR de verificación).
- Subido a Cloudflare R2 `certificates/` con URL firmada.
- Vista previa en modal + descarga + compartir en LinkedIn.

---

## 10. Panel de organización (hospital_admin)

### 10.1 Gestión de empleados (`/org/employees`)
- **Código de invitación:** enlace único con `org_code` para que empleados se registren directamente vinculados a la organización.
- **Invitación por email:** `hospital_admin` ingresa email → se envía invitación (expira en 7 días).
- **Cambiar rol:** ascender/descender entre `student` ↔ `hospital_admin`.
- **Protección de admin único:** imposible dejar una organización sin al menos un `hospital_admin` activo. Intentar remover o descender al único admin se bloquea.
- **Remover empleado:** revoca `EmployeeAssignment`, libera el cupo. No borra `Enrollment` ni certificados.

### 10.2 Reportes de progreso (`/org/reports`)
- Tabla empleado × curso × progreso con resumen agregado.
- Exportación a CSV.
- Filtro por curso.

---

## 11. Reembolsos

### 11.1 Política de elegibilidad
- **Ventana:** 7 días desde la compra.
- **Progreso máximo:** 20% del curso.
- **Para experiencias VR:** solo aplica ventana de 7 días (no hay progreso medible). Si el código VR ya fue redimido, pasa a revisión manual obligatoria.
- Centralizada en `lib/refunds/policy.ts` — fuente única de verdad, nunca duplicada.

### 11.2 Flujo
1. Estudiante solicita desde `/orders` (botón visible solo si es elegible).
2. `super_admin` revisa en `/admin/refunds`.
3. Si aprueba → reversa transacción vía Wompi → revoca acceso → email de confirmación.
4. Si rechaza → motivo obligatorio → email al estudiante.
5. Para compras corporativas, solo el `hospital_admin` puede solicitar el reembolso (no empleados individuales).
6. Reembolsos parciales por cupo no soportados en la fase actual.

---

## 12. Soporte

- Formulario en `/soporte`, accesible con o sin sesión.
- Categorías: problema de pago, problema técnico, pregunta sobre certificado, otro.
- Selector opcional de orden/curso relacionado para dar contexto al equipo.
- Respuesta por email en menos de 48 horas.
- Enlace visible en footer y menú de usuario.

---

## 13. Seguridad

### 13.1 Row Level Security (RLS)
- Aislamiento multi-tenant en Postgres: cada usuario solo ve datos de su organización.
- 29+ policies en tablas principales, más policies nuevas para Course Builder y Vendor.
- Helpers: `requesting_user_id()`, `get_user_org_id()`.
- Test de aislamiento cross-org obligatorio antes de habilitar pagos reales.

### 13.2 Protección de datos sensibles
- Datos bancarios de vendors cifrados con AES-256-GCM (`VENDOR_BANK_ENCRYPTION_KEY`).
- URLs firmadas con expiración para certificados e invoices.
- Video siempre vía manifiesto HLS firmado, nunca URL descargable directa.
- Cumplimiento Ley 1581 de Habeas Data (Colombia).

### 13.3 Seguridad en pagos
- Webhook de Wompi validado con HMAC-SHA256.
- Idempotencia: mismo evento dos veces no duplica inscripción ni orden.
- `MOODLE_WS_TOKEN`, `WOMPI_PRIVATE_KEY`, `WOMPI_EVENTS_SECRET` y demás secretos nunca expuestos en cliente.

---

## 14. Stack de infraestructura

| Componente | Detalle |
|---|---|
| VPS | Hetzner CX22 (2 vCPU, 4 GB RAM, 40 GB SSD) o similar |
| SO | Ubuntu 24.04 LTS |
| Firewall | UFW (solo puertos 22, 80, 443) |
| SSL | Let's Encrypt + Certbot (renovación automática) |
| Monitoreo | UptimeRobot → `/api/health` |
| Backups | Script `backup-db.sh` con cron diario en VPS |
| Error tracking | Sentry (free tier) |

---

## 15. Cumplimiento y regulación

- **Ley 1581 de 2012 (Habeas Data):** protección de datos personales en Colombia.
- **Facturación electrónica DIAN:** datos de NIT/CC en checkout. Facturación electrónica completa en Fase 13.
- **Banner de cookies** con consentimiento explícito (vanilla-cookieconsent).
- **Política de privacidad** accesible desde el footer.

---

## 16. Estado actual del proyecto (julio 2026)

| Fase | Estado |
|---|---|
| Fase 1 — Fundaciones | ✅ Completa |
| Fase 2 — Landing + Auth | ✅ Completa |
| Fase 2.5 — CI/CD + VPS | ~ En progreso (CI listo, VPS pendiente) |
| Fase 3 — Marketplace | ✅ Completa |
| Fase 4 — Carrito + Checkout (Wompi) | ✅ Completa |
| Fase 5 — Dashboard del Estudiante | ✅ Completa |
| Fase 6 — Integración Moodle | ✅ Completa |
| Fase 6.5 — Course Builder + Multi-Vendor | ✅ Completa |
| Fase 7 — Panel de Organización | ⬜ Pendiente |
| Fase 7.1 — Reembolsos y Soporte | ⬜ Pendiente |
| Fases 8-13 | ⬜ Pendientes |

---

## 17. Glosario

| Término | Definición |
|---|---|
| **Course Builder** | Herramienta de creación de cursos dentro de Medicamentum360. |
| **Drip content** | Contenido que se desbloquea N días después de la inscripción del estudiante. |
| **Vendor** | Instructor o estudio VR externo que vende en el marketplace. |
| **KYC** | Know Your Customer — verificación de identidad y datos fiscales del vendor. |
| **RLS** | Row Level Security — aislamiento de datos a nivel de fila en Postgres. |
| **HLS** | HTTP Live Streaming — protocolo de streaming adaptativo usado por Cloudflare Stream. |
| **SSO** | Single Sign-On — autenticación única entre Medicamentum360 y Moodle. |
| **Payout** | Pago de comisiones al vendor por ventas de sus productos. |
| **EmployeeAssignment** | Asignación de un cupo de curso a un empleado de una organización. |
| **Enrollment** | Inscripción de un estudiante en un curso, con tracking de progreso. |
