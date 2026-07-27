/**
 * Dr. Medici — Embed Snippet para Medicamentum360
 * 
 * Uso:
 * 1. Copia este script en tu página (ej. layout.tsx de Next.js)
 * 2. Ajusta N8N_WEBHOOK_URL con la URL real de tu webhook n8n
 * 3. El widget de chat aparecerá automáticamente
 * 
 * Ejemplo en Next.js App Router (layout.tsx):
 * 
 *   import Script from 'next/script';
 *   export default function Layout({ children }) {
 *     return (
 *       <html>
 *         <body>
 *           {children}
 *           <Script src="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js" />
 *           <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css" />
 *           <Script id="dr-medici-widget" strategy="afterInteractive">
 *             {`
 *               window.N8N_WEBHOOK_URL = 'https://n8n.tudominio.com/webhook/dr-medici-chat';
 *             `}
 *           </Script>
 *           <Script src="/widget/dr-medici-init.js" strategy="afterInteractive" />
 *         </body>
 *       </html>
 *     )
 *   }
 */

(function() {
  'use strict';

  // Esperar a que el SDK de n8n esté disponible
  function initDrMedici() {
    if (typeof window.createChat === 'undefined') {
      setTimeout(initDrMedici, 200);
      return;
    }

    const webhookUrl = window.N8N_WEBHOOK_URL ||
      'http://localhost:5678/webhook/dr-medici-chat';

    window.createChat({
      webhookUrl: webhookUrl,
      webhookConfig: {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      },
      target: '#n8n-chat',
      mode: 'window',
      chatInputKey: 'chatInput',
      chatSessionKey: 'sessionId',
      metadata: {
        page: window.location.pathname,
        userAgent: navigator.userAgent,
      },
      showWelcomeScreen: true,
      defaultLanguage: 'es',
      initialMessages: [
        '¡Hola! 👋 Soy **Dr. Medici** 🩺, el asistente virtual de Medicamentum360.',
        '¿En qué te puedo ayudar hoy?'
      ],
      i18n: {
        es: {
          title: 'Dr. Medici 🩺',
          subtitle: 'Asistente Virtual de Medicamentum360',
          footer: '',
          getStarted: 'Nueva Conversación',
          inputPlaceholder: 'Escribe tu consulta aquí...',
          sendButtonText: 'Enviar',
          closeButtonText: 'Cerrar',
        },
      },
    });
  }

  // Iniciar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDrMedici);
  } else {
    initDrMedici();
  }
})();
