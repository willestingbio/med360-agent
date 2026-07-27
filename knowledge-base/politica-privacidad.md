# Política de Privacidad — Medicamentum360

**Última actualización:** 27 de julio de 2026
**Versión:** 1.0

---

## 1. Identidad del Responsable del Tratamiento

**Medicamentum360** es una plataforma SaaS de e-learning y marketplace para el sector salud, operada por:

- **Razón social:** [Nombre legal de la empresa operadora]
- **NIT:** [NIT de la empresa]
- **Domicilio:** Colombia
- **Correo electrónico de contacto:** privacidad@medicamentum360.com
- **Sitio web:** https://medicamentum360.com

---

## 2. Marco Legal

Esta política de privacidad se rige por las siguientes disposiciones:

- **Ley 1581 de 2012** — Ley de Protección de Datos Personales (Habeas Data) de la República de Colombia.
- **Decreto 1377 de 2013** — Reglamentación parcial de la Ley 1581.
- **Ley 1266 de 2008** — Disposiciones generales del Habeas Data financiero.
- **Resolución 00564 de 2012** de la Superintendencia de Industria y Comercio (SIC).

---

## 3. Datos Personales que Recolectamos

### 3.1 Datos proporcionados por el Usuario

| Categoría | Datos | Finalidad |
|---|---|---|
| **Identificación** | Nombres, apellidos, correo electrónico | Creación de cuenta, comunicación, soporte |
| **Perfil profesional** | Cargo, especialidad, organización/institución (opcional) | Personalización de la experiencia en la plataforma |
| **Autenticación** | Contraseña (hash cifrado), tokens de sesión | Acceso seguro a la plataforma |
| **Facturación** | Tipo de documento (NIT/CC), número de documento | Emisión de facturas, cumplimiento fiscal DIAN |
| **Pago** | Información de tarjeta de crédito/débito | **Nota importante:** Medicamentum360 NO almacena datos de tarjetas. El pago se procesa exclusivamente a través de Wompi (widget embebido seguro). |
| **Contenido generado** | Cursos creados, quizzes, preguntas, respuestas a quizzes | Operación de la plataforma como marketplace de formación |
| **Soporte** | Asunto, descripción del problema, orden/curso relacionado (opcional) | Resolución de tickets de soporte |

### 3.2 Datos recolectados automáticamente

| Categoría | Datos | Finalidad |
|---|---|---|
| **Navegación** | Páginas visitadas, tiempo en la plataforma, interacciones | Análisis de uso, mejora del producto |
| **Dispositivo** | Tipo de navegador, sistema operativo, resolución de pantalla | Compatibilidad y optimización de la experiencia |
| **Ubicación** | Dirección IP (anonimizada) | Seguridad, prevención de fraude, cumplimiento fiscal |
| **Cookies** | Cookies técnicas, de sesión y de preferencias | Funcionamiento de la plataforma, recordar preferencias |

### 3.3 Datos sensibles

Medicamentum360 puede recolectar datos considerados sensibles según la legislación colombiana:

- **Datos de salud/educación:** inferidos por el tipo de cursos que consumes (formación médica). Estos datos se usan exclusivamente para recomendarte contenido relevante y generar tus certificados de formación continua.
- **Datos fiscales/bancarios de vendors:** los creadores de contenido que venden en el marketplace proporcionan datos fiscales (NIT, certificado bancario) y de cuenta bancaria. Estos datos se **cifran con AES-256-GCM** a nivel de aplicación antes de ser almacenados y solo se desencriptan durante el proceso automatizado de pago de comisiones.

---

## 4. Finalidad del Tratamiento

Los datos personales recolectados se utilizan para:

1. **Crear y gestionar tu cuenta** de usuario en la plataforma.
2. **Procesar tus compras** de cursos, experiencias VR y otros productos.
3. **Emitir facturas electrónicas** conforme a los requisitos de la DIAN.
4. **Proveer acceso al contenido** que has adquirido (lecciones, videos, recursos descargables).
5. **Generar certificados** de finalización de cursos con validez verificable.
6. **Enviar comunicaciones transaccionales** (confirmaciones de compra, recordatorios, notificaciones de la plataforma).
7. **Brindar soporte técnico** y resolver tus consultas.
8. **Mejorar la plataforma** mediante análisis de uso agregado y anonimizado.
9. **Prevenir fraude** y garantizar la seguridad de la plataforma.
10. **Cumplir obligaciones legales** (fiscales, contables, de protección al consumidor).
11. **Gestionar el marketplace multi-vendor:** calcular y procesar pagos de comisiones a creadores.
12. **Gestión de organizaciones:** permitir que los administradores de hospitales asignen y monitoreen la capacitación de sus empleados.

---

## 5. Datos de Terceros

### 5.1 Datos de empleados gestionados por una organización

Cuando un `hospital_admin` crea o gestiona empleados en la plataforma:

- El administrador proporciona nombres y correos electrónicos de sus empleados para invitarlos.
- El empleado, al aceptar la invitación, consiente el tratamiento de sus datos conforme a esta política.
- El administrador de la organización puede ver el nombre, email y progreso académico de los empleados bajo su gestión.
- El empleado conserva control sobre su cuenta personal y puede solicitar la eliminación de sus datos en cualquier momento.

### 5.2 Datos de vendors/creadores externos

Los instructores y estudios VR que venden en el marketplace:

- Proporcionan datos fiscales y bancarios que se almacenan cifrados.
- El nombre público del vendor (`displayName`) es visible en el marketplace.
- Los datos de ventas y comisiones son visibles para el vendor en su panel.
- Los compradores NO tienen acceso a datos personales del vendor más allá de su nombre público.

---

## 6. Transferencia y Transmisión de Datos

### 6.1 Proveedores de servicios (encargados del tratamiento)

| Proveedor | País | Datos compartidos | Finalidad |
|---|---|---|---|
| **Wompi** (Bancolombia) | Colombia | Datos de pago (procesados, no almacenados por nosotros) | Procesamiento de pagos y reembolsos |
| **Brevo** (Sendinblue) | Francia / UE | Correo electrónico, nombre | Envío de emails transaccionales |
| **Cloudflare** (R2 y Stream) | Global | Archivos de contenido (imágenes, PDFs, certificados, videos) | Almacenamiento y distribución de contenido |
| **Better Auth** | Self-hosted (nuestro VPS) | Credenciales de acceso (hash) | Autenticación de usuarios |
| **Google** (OAuth) | EE.UU. | Email, nombre (solo si usas "Iniciar sesión con Google") | Autenticación |
| **Moodle** (LMS) | Self-hosted (nuestro VPS) | Email, nombre, ID de usuario | Sincronización de inscripciones y progreso |
| **Sentry** | EE.UU. | Datos de errores técnicos (anonimizados) | Monitoreo de estabilidad de la plataforma |
| **Hetzner/Contabo/DigitalOcean** | Alemania / EE.UU. | Datos del servidor (infraestructura) | Hosting de la plataforma |

### 6.2 Transferencia internacional de datos

Algunos de nuestros proveedores operan en servidores fuera de Colombia. Al usar Medicamentum360, aceptas que tus datos puedan ser transferidos y procesados en países que pueden tener estándares de protección de datos diferentes a los colombianos. En todos los casos, exigimos contractualmente a nuestros proveedores que cumplan con estándares de seguridad equivalentes o superiores a los exigidos por la legislación colombiana.

### 6.3 Datos que NO compartimos

- **No vendemos** datos personales a terceros.
- **No compartimos** datos de tarjetas de crédito/débito con nadie.
- **No compartimos** datos de progreso académico individual con terceros ajenos a tu organización (si perteneces a una).
- **No compartimos** datos bancarios de vendors en texto plano, ni siquiera con administradores internos.

---

## 7. Derechos del Titular (Ley 1581 de 2012)

Como titular de datos personales, tienes los siguientes derechos:

### 7.1 Derecho de Acceso
Puedes solicitar en cualquier momento conocer qué datos personales tuyos tenemos almacenados. Esta información está disponible en tu panel de `/configuracion`.

### 7.2 Derecho de Actualización y Rectificación
Puedes corregir, actualizar o completar tus datos personales desde `/configuracion` → Perfil. Si un dato no es editable desde la interfaz, contáctanos.

### 7.3 Derecho de Supresión (Derecho al Olvido)
Puedes solicitar la eliminación total de tus datos personales. Ve a `/configuracion` → "Eliminar cuenta". Esta acción:
- Elimina tus datos personales de nuestros sistemas activos.
- **No elimina** registros de transacciones financieras que debemos conservar por ley (5 años para fines fiscales en Colombia).
- **No elimina** certificados ya emitidos (se anonimizan pero se conservan para verificabilidad).
- Si eres vendor, tus productos se despublican pero los estudiantes que ya los compraron mantienen acceso.

### 7.4 Derecho de Revocatoria del Consentimiento
Puedes revocar tu consentimiento para el tratamiento de datos en cualquier momento. Esto puede implicar la imposibilidad de seguir usando servicios que requieren dichos datos (ej. no podemos emitir un certificado sin tu nombre).

### 7.5 Derecho de Oposición
Puedes oponerte al tratamiento de tus datos para finalidades específicas, como comunicaciones de marketing (no realizamos marketing sin consentimiento explícito previo).

### 7.6 Procedimiento para ejercer tus derechos

Envía tu solicitud a **privacidad@medicamentum360.com** con:
- Nombre completo
- Correo electrónico asociado a tu cuenta
- Derecho que deseas ejercer
- Descripción clara de tu solicitud

Responderemos en un máximo de **10 días hábiles** (plazo legal según Ley 1581). Si la solicitud es compleja, podemos extender el plazo a 15 días hábiles, notificándote antes.

---

## 8. Seguridad de los Datos

### 8.1 Medidas técnicas

| Medida | Descripción |
|---|---|
| **Cifrado en tránsito** | Toda comunicación entre tu navegador y nuestros servidores viaja cifrada mediante TLS 1.3 (HTTPS). |
| **Cifrado en reposo** | Datos bancarios de vendors cifrados con AES-256-GCM. Contraseñas hasheadas con algoritmos modernos (bcrypt/argon2). |
| **Aislamiento multi-tenant** | Row Level Security (RLS) en Postgres: cada usuario solo puede acceder a sus propios datos y los de su organización. |
| **Autenticación robusta** | Better Auth con 2FA opcional (TOTP). Sesiones con expiración. Rate limiting contra ataques de fuerza bruta. |
| **Acceso mínimo** | El personal de Medicamentum360 accede a datos solo cuando es estrictamente necesario para soporte u operación. |
| **Backups cifrados** | Las copias de seguridad de la base de datos se almacenan cifradas. |
| **Monitoreo** | Logs de acceso y actividad para detección de anomalías. |

### 8.2 Medidas organizativas

- Todo el personal con acceso a datos firma acuerdos de confidencialidad.
- Capacitación periódica en protección de datos personales.
- Evaluaciones de impacto de privacidad para nuevos features.
- Notificación de brechas de seguridad a la SIC y a los titulares afectados en un máximo de 15 días hábiles.

---

## 9. Cookies y Tecnologías de Rastreo

### 9.1 Cookies técnicas (esenciales)
- **Sesión:** necesarias para mantener tu sesión activa mientras usas la plataforma.
- **Carrito:** almacenamiento local en tu navegador para recordar productos agregados al carrito (incluso sin sesión iniciada).
- **Tema:** recordar tu preferencia de modo claro/oscuro.
- **Idioma:** recordar tu preferencia de idioma.

Estas cookies no requieren consentimiento porque son esenciales para el funcionamiento del servicio.

### 9.2 Cookies de preferencias
- **Tema (dark/light/system):** se almacena en `localStorage` para persistir tu elección visual.
- **Última lección visitada:** para que la plataforma te redirija a "continuar donde lo dejaste".

### 9.3 Cookies de analítica
- Google Analytics 4 (GA4) o Posthog, configurados con anonimización de IP. Se usan exclusivamente para entender cómo se usa la plataforma y mejorarla.

### 9.4 Gestión de cookies
Al visitar el sitio por primera vez, verás un banner de cookies donde puedes aceptar o rechazar cookies no esenciales. Puedes cambiar tu configuración en cualquier momento desde `/configuracion` o desde la configuración de tu navegador.

---

## 10. Conservación de Datos

| Tipo de dato | Periodo de conservación |
|---|---|
| Datos de cuenta activa | Mientras la cuenta esté activa |
| Certificados emitidos | Indefinido (para verificabilidad, anonimizados si la cuenta se elimina) |
| Historial de compras y facturas | 5 años (obligación fiscal colombiana) |
| Tickets de soporte | 2 años desde su cierre |
| Datos de vendors (incluyendo fiscales) | 5 años desde la última transacción (obligación fiscal) |
| Logs técnicos | 90 días (rotación automática) |
| Datos en backups | 30 días (rotación de backups) |

---

## 11. Menores de Edad

Medicamentum360 no está dirigido a menores de 18 años. Si eres padre/madre o tutor y descubres que tu hijo menor de edad nos ha proporcionado datos personales sin tu consentimiento, contáctanos para eliminarlos.

---

## 12. Cambios a esta Política

Cualquier cambio a esta política será:
1. Publicado en esta página con una nueva fecha de "última actualización".
2. Notificado por correo electrónico a los usuarios registrados con al menos 15 días de anticipación si los cambios son sustanciales.
3. Sujeto a tu aceptación antes de seguir usando la plataforma si los cambios afectan la finalidad del tratamiento de forma significativa.

---

## 13. Contacto y Reclamos

### 13.1 Responsable del tratamiento
- **Correo:** privacidad@medicamentum360.com
- **Dirección:** [Dirección física en Colombia]
- **Teléfono:** [Teléfono de contacto]

### 13.2 Reclamos ante la autoridad de control
Si consideras que tus derechos de protección de datos han sido vulnerados, puedes presentar un reclamo ante:

**Superintendencia de Industria y Comercio (SIC)**
- Delegatura para la Protección de Datos Personales
- Sitio web: https://www.sic.gov.co
- Línea gratuita nacional: 01 8000 910165

---

## 14. Aceptación

Al registrarte y usar Medicamentum360, declaras haber leído y comprendido esta Política de Privacidad y autorizas el tratamiento de tus datos personales conforme a lo aquí descrito, en cumplimiento de la Ley 1581 de 2012.
