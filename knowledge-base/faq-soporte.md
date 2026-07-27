# FAQ de Soporte — Medicamentum360

**Versión:** 1.0 · **Fecha:** 2026-07-27
**Propósito:** Respuestas a preguntas frecuentes para agentes de IA y equipo de soporte.

---

## Índice
- [Cuenta y acceso](#cuenta-y-acceso)
- [Compras y pagos](#compras-y-pagos)
- [Cursos y contenido](#cursos-y-contenido)
- [Certificados](#certificados)
- [Organizaciones y empleados](#organizaciones-y-empleados)
- [Vendors y creadores](#vendors-y-creadores)
- [Problemas técnicos](#problemas-tecnicos)
- [Reembolsos y garantía](#reembolsos-y-garantia)
- [Privacidad y datos](#privacidad-y-datos)

---

## Cuenta y acceso

### ¿Cómo me registro?
Ve a `/sign-up`. Puedes registrarte con tu email y contraseña, o usar "Continuar con Google". Si tu hospital te envió un enlace de invitación, ábrelo directamente y sigue los pasos; quedarás vinculado automáticamente a tu organización.

### ¿Qué hago si no recibo el email de verificación?
1. Revisa tu carpeta de spam o correo no deseado.
2. Si no aparece, en la pantalla de verificación hay un botón "Reenviar email de verificación".
3. Si el problema persiste, contacta a soporte en `/soporte`.

### ¿Puedo cambiar mi contraseña?
Sí. Ve a `/configuracion` → sección Seguridad → "Cambiar contraseña". También puedes usar "¿Olvidaste tu contraseña?" en la pantalla de inicio de sesión.

### ¿Ofrecen autenticación de dos factores (2FA)?
Sí. Actívala en `/configuracion` → Seguridad. Usa una app de autenticación tipo Google Authenticator o Authy para escanear el código QR.

### Olvidé mi contraseña, ¿qué hago?
1. Ve a `/sign-in` → "¿Olvidaste tu contraseña?".
2. Ingresa tu email y recibirás un enlace de restablecimiento.
3. Si no recibes el email, revisa spam o contacta a soporte.
4. El enlace expira tras un tiempo; si caduca, puedes solicitar uno nuevo.

### Mi cuenta dice "no verificada", ¿qué significa?
Necesitas verificar tu correo electrónico antes de acceder al dashboard. Revisa tu bandeja de entrada (incluyendo spam) para el email de verificación.

### ¿Puedo iniciar sesión con Google y también con email?
Sí. Si te registraste con Google, puedes seguir usando ese método. Si quieres también usar email y contraseña, contacta a soporte para vincular ambos métodos.

---

## Compras y pagos

### ¿Qué métodos de pago aceptan?
Procesamos pagos a través de Wompi, que acepta tarjetas de crédito/débito (Visa, Mastercard, American Express), transferencias bancarias PSE (para Colombia), Nequi, y otros medios locales colombianos. Los métodos disponibles se muestran en el widget de Wompi durante el checkout.

### ¿Mis datos de pago están seguros?
Sí. Medicamentum360 **nunca almacena** los datos de tu tarjeta. El pago se procesa directamente en los servidores de Wompi usando su widget embebido seguro (Checkout Brick). Nuestra conexión con Wompi está cifrada y validada con HMAC-SHA256.

### ¿Recibo factura por mi compra?
Sí. Al completar una compra recibirás un email de confirmación con el resumen de tu orden. Las facturas en formato PDF están disponibles en `/configuracion` → Historial de compras. Los datos de facturación (NIT o CC) se solicitan durante el checkout.

### Hice un pago pero el curso no aparece en Mi Aprendizaje
Esto puede ocurrir si el webhook de confirmación de Wompi tarda en llegar. Sigue estos pasos:
1. Espera unos minutos y recarga la página.
2. Si el curso sigue sin aparecer después de 30 minutos, contacta a soporte indicando el número de referencia de tu transacción de Wompi.
3. El equipo verificará tu orden y activará tu acceso manualmente.

### Recibí un cobro duplicado, ¿qué hago?
El sistema tiene protección de idempotencia: aunque el webhook de Wompi se reciba dos veces, no se duplica la inscripción. Si ves dos cobros en tu extracto bancario:
1. Espera 24-48 horas; a veces los cobros duplicados son retenciones temporales que el banco libera automáticamente.
2. Si ambos montos se efectivizan, contacta a soporte con los comprobantes.

### ¿Puedo pagar para otra persona?
Sí. Puedes comprar un curso y luego contactar a soporte para transferir el acceso. Sin embargo, si eres `hospital_admin`, el flujo correcto es usar la opción "Comprar para mi organización" y luego asignar los cupos a tus empleados desde `/org/employees`.

---

## Cursos y contenido

### ¿Cómo accedo a un curso que compré?
- **Cursos creados en Medicamentum360:** ve a `/dashboard` → Mis Cursos → selecciona el curso. El contenido se reproduce directamente en la plataforma.
- **Cursos legacy vinculados a Moodle:** al hacer clic en "Continuar curso", serás redirigido automáticamente a `lms.medicamentum360.com` con inicio de sesión automático (SSO).

### El video de una lección no carga, ¿qué hago?
1. Verifica tu conexión a internet.
2. Intenta recargar la página.
3. Si el reproductor muestra error, usa el botón "Reintentar" que aparece en el reproductor.
4. Si el problema persiste en varias lecciones del mismo curso, contacta a soporte indicando el nombre del curso y la lección específica.

### ¿Por qué algunas lecciones aparecen con candado?
Puede ser por dos razones:
1. **No has completado las lecciones anteriores** (algunos cursos tienen orden secuencial obligatorio, aunque la mayoría te permite navegar libremente).
2. **Drip content:** la lección pertenece a un módulo que se desbloquea N días después de tu inscripción. Verás la fecha exacta de desbloqueo junto al candado.

### No aprobé un quiz, ¿cuántos intentos tengo?
Depende de la configuración del curso. Algunos quizzes tienen intentos ilimitados, otros tienen un máximo (por ejemplo, 3 intentos). Esta información se muestra en la pantalla del quiz antes de empezar y en la pantalla de resultados. Si agotaste todos los intentos y no aprobaste, contacta a soporte para que un instructor revise tu caso.

### ¿Cómo funciona el drip content (contenido por goteo)?
Algunos cursos liberan el contenido de forma gradual. Por ejemplo, el "Módulo 2" puede configurarse para desbloquearse 7 días después de tu inscripción, aunque hayas completado todo el Módulo 1. Esto permite que el aprendizaje sea espaciado y progresivo. Verás el candado con la fecha exacta de desbloqueo.

### Descargué un recurso (PDF) y no se abre
Asegúrate de tener un lector de PDF instalado. Si el enlace expiró (las descargas usan URLs firmadas con tiempo limitado), regresa a la lección y vuelve a hacer clic en el recurso para generar un nuevo enlace de descarga.

---

## Certificados

### ¿Cuándo recibo mi certificado?
Al completar el 100% de las lecciones del curso y aprobar los quizzes obligatorios (si los hay), el certificado se habilita automáticamente. Ve a `/dashboard` → Mis Certificados y haz clic en "Generar certificado".

### ¿Puedo generar un certificado varias veces?
Una vez generado, el certificado queda almacenado. Puedes descargarlo cuantas veces quieras desde Mis Certificados. El sistema no regenera un certificado nuevo cada vez; recupera el existente.

### ¿Los certificados incluyen verificación?
Sí. Cada certificado incluye un código QR único que permite verificar su autenticidad. Quien escanee el QR puede confirmar que el certificado fue emitido por Medicamentum360 y corresponde a un curso completado.

### ¿Puedo compartir mi certificado en LinkedIn?
Sí. En el modal de vista previa del certificado, hay un botón "Compartir en LinkedIn" que genera un enlace con los campos pre-rellenados (nombre del curso, fecha, emisor).

### Perdí mi certificado, ¿puedo recuperarlo?
Sí. Mientras tu cuenta esté activa, puedes volver a `/dashboard` → Mis Certificados y descargarlo de nuevo en cualquier momento.

---

## Organizaciones y empleados

### Soy administrador de un hospital, ¿cómo invito a mis empleados?
Ve a `/org/employees`. Tienes dos opciones:
1. **Código de invitación:** copia el enlace `https://medicamentum360.com/sign-up?org_code=TUCODIGO` y compártelo con tus empleados. Al registrarse con ese enlace, quedarán vinculados automáticamente a tu organización.
2. **Invitación por email:** ingresa el correo del empleado y haz clic en "Invitar". Recibirá un email con el enlace de registro.

### Compré cupos para mis empleados pero no aparecen en el panel
Los cupos comprados no se asignan automáticamente. Después de comprar, debes ir a `/org/employees` y usar el botón "Asignar curso" junto al nombre de cada empleado para asignarle un cupo. El banner superior te mostrará cuántos cupos tienes disponibles sin asignar.

### Asigné un cupo pero el empleado no puede acceder al curso
Verifica que:
1. El empleado haya aceptado la invitación y completado su registro en la plataforma.
2. El `EmployeeAssignment` esté en estado `active` (no `revoked`).
3. El empleado haya iniciado sesión con la misma cuenta vinculada a la organización.

Si todo está correcto y el problema persiste, contacta a soporte.

### ¿Cómo revoco el acceso de un empleado que dejó el hospital?
Ve a `/org/employees`, busca al empleado y en el menú `⋮` selecciona "Remover de la organización". Esto:
- Le quita el acceso inmediato a los cursos comprados por la organización.
- **No** borra su cuenta personal ni los certificados que ya obtuvo.
- **No** afecta cursos que haya comprado con su propio dinero.
- Libera el cupo para que puedas asignarlo a otro empleado.

### ¿Puedo cambiar un empleado de "Estudiante" a "Administrador"?
Sí. En `/org/employees`, usa el dropdown de rol junto al nombre del empleado. Ten en cuenta que no puedes cambiar tu propio rol, y siempre debe haber al menos un `hospital_admin` en la organización.

### ¿Cómo exporto el progreso de mis empleados?
Ve a `/org/reports`. Verás una tabla con el progreso de cada empleado por curso. Usa el botón "Exportar CSV" para descargar los datos en formato hoja de cálculo.

---

## Vendors y creadores

### Quiero vender mis cursos en Medicamentum360, ¿cómo empiezo?
1. Regístrate como usuario normal si aún no tienes cuenta.
2. Ve a `/vender` y completa el formulario de registro como creador (nombre público, bio).
3. Completa tus datos fiscales y bancarios para recibir pagos.
4. El equipo de Medicamentum360 revisará tu perfil (máximo 48 horas).
5. Una vez aprobado, accede a `/instructor` para crear tu primer curso.

### ¿Cuánto me pagan por cada venta?
Medicamentum360 retiene una comisión del **20%** sobre cada venta de tus productos. Recibes el 80% restante. El pago se realiza mensualmente mediante transferencia bancaria a través de Wompi.

### ¿Cada cuánto recibo mis pagos?
Los pagos (payouts) se calculan mensualmente. Al final de cada mes, se genera un lote con tus ventas del periodo, se descuenta la comisión y, tras revisión del equipo, se transfiere el monto neto a tu cuenta bancaria.

### Mi producto fue rechazado en revisión, ¿qué hago?
Recibirás un email con el motivo del rechazo. Puedes editar tu producto en `/instructor` para corregir lo señalado y volver a enviarlo a revisión. No es necesario crear un producto nuevo.

### ¿Puedo ver quién compró mis cursos?
No. Por privacidad de los estudiantes, los vendors no tienen acceso a información personal de los compradores. Sí puedes ver métricas agregadas: número de ventas, ingresos generados y progreso general de los estudiantes en tus cursos a través de las estadísticas de cada curso.

### Suspendieron mi cuenta de vendor, ¿qué pasó?
Las suspensiones pueden ocurrir por contenido que no cumple los estándares de calidad, incumplimiento de los términos de uso, o a solicitud propia. Recibirás un email con el motivo. Para apelar una suspensión, contacta a soporte.

### Si me suspenden, ¿los estudiantes que ya compraron pierden el acceso?
No. Los estudiantes que ya adquirieron tus cursos mantienen su acceso al contenido. La suspensión solo impide nuevas ventas de tus productos.

### ¿Mis datos bancarios están seguros?
Sí. La información de tu cuenta bancaria se almacena cifrada con AES-256-GCM (estándar militar) y nunca es visible en texto plano, ni siquiera para los administradores de la plataforma. Solo el proceso automatizado de payout la desencripta para realizar la transferencia.

---

## Problemas técnicos

### La página no carga o va muy lenta
1. Verifica tu conexión a internet.
2. Intenta recargar la página (Ctrl+F5 o Cmd+Shift+R para limpiar caché).
3. Si el problema persiste, prueba desde otro navegador o dispositivo.
4. Reporta el problema en `/soporte` indicando qué página intentabas visitar y qué error ves.

### Error "No autorizado" al intentar acceder a una página
Esto suele ocurrir cuando:
- Tu sesión expiró. Cierra sesión y vuelve a iniciarla.
- Intentas acceder a una sección que requiere un rol específico (ej. panel de administrador siendo estudiante).
- Tu acceso fue revocado (por ejemplo, si tu organización te removió).
Si crees que deberías tener acceso, contacta a soporte.

### Error "Algo salió mal" durante una compra
- Verifica que los datos de tu tarjeta sean correctos.
- Asegúrate de tener fondos suficientes.
- El widget de Wompi debería mostrar un mensaje más específico sobre el error. Si el error es genérico, reintenta en unos minutos.
- Si el problema persiste, contacta a soporte.

### El certificado no se genera
Esto puede pasar si el servidor de generación de PDF encuentra un error. Intenta de nuevo desde `/dashboard` → Mis Certificados. Si falla repetidamente, contacta a soporte indicando el nombre del curso.

### Problemas de visualización en tablet (iPad)
Medicamentum360 está diseñado para ser responsive, con soporte específico para tablets (caso de uso común en hospitales). Si encuentras problemas de visualización:
1. Asegúrate de tener el navegador actualizado.
2. Prueba en orientación horizontal si la vertical no se ve bien en algunas pantallas.
3. Reporta el problema indicando modelo de tablet y navegador.

---

## Reembolsos y garantía

### ¿Cuál es la política de reembolso?
Tienes **7 días** desde la fecha de compra para solicitar un reembolso, siempre que hayas completado **menos del 20%** del curso. Para experiencias VR, solo aplica la ventana de 7 días.

### ¿Cómo solicito un reembolso?
Ve a `/orders` (historial de compras). Si tu orden es elegible (dentro de 7 días y menos de 20% de progreso), verás un botón "Solicitar reembolso". Selecciona el motivo de tu solicitud y envíala. El equipo la revisará y te responderá.

### Si ya completé más del 20% del curso, ¿puedo pedir reembolso igual?
Puedes enviar la solicitud, pero no será aprobada automáticamente. Pasará a revisión manual del equipo de Medicamentum360, que evaluará tu caso (por ejemplo, si hubo un problema técnico legítimo que te impidió avanzar). No hay garantía de aprobación fuera de la política estándar.

### ¿Cuánto tarda el reembolso?
Una vez aprobado, el reembolso se procesa a través de Wompi. El tiempo que tarda en reflejarse en tu cuenta depende de tu banco (generalmente 5-10 días hábiles).

### Compré un curso para mi organización, ¿cómo solicito reembolso?
Solo el `hospital_admin` de la organización puede solicitar el reembolso de una compra corporativa, desde su panel de órdenes. Los empleados individuales con cupos asignados no pueden solicitar reembolsos de compras que hizo la organización.

### ¿Hay reembolso parcial si solo usé algunos cupos de una compra en lote?
Actualmente el reembolso aplica a la orden completa, no a cupos individuales sin usar. Si compraste 10 cupos y solo asignaste 3, el reembolso sería por la orden completa (reembolsando los 7 cupos sin usar y revocando el acceso de los 3 asignados). Si necesitas reembolso solo de los cupos sin usar, contacta a soporte directamente para evaluar tu caso.

---

## Privacidad y datos

### ¿Qué datos personales recolectan?
Recolectamos nombre, apellidos, email, cargo/especialidad (opcional), datos de facturación (NIT o CC para emitir factura), y foto de perfil (opcional). Cumplimos con la Ley 1581 de 2012 (Habeas Data) de Colombia. Detalles completos en nuestra Política de Privacidad.

### ¿Cómo elimino mi cuenta?
Ve a `/configuracion` → sección "Zona de peligro" → "Eliminar cuenta". Esta acción es irreversible. Si tienes cursos comprados, perderás el acceso a ellos. Si eres vendor, se cancelarán tus productos publicados.

### ¿Comparten mis datos con terceros?
Tus datos de pago nunca se comparten (se procesan directamente en Wompi). Tus datos personales no se venden ni comparten con terceros no esenciales para la operación de la plataforma. Para el caso de organizaciones, tu `hospital_admin` puede ver tu nombre, email y progreso en los cursos asignados por la organización.

### ¿Por cuánto tiempo guardan mis datos?
Tus datos se conservan mientras tu cuenta esté activa. Al eliminar tu cuenta, los datos personales se eliminan, pero se conservan registros anonimizados de transacciones y certificados emitidos por obligaciones fiscales y de auditoría.
