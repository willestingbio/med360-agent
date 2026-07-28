"""
medicalMen — Agente IA de Medicamentum360
==========================================
Chatbot con RAG (Groq + Llama 3.3 70B) para el Challenge Alura Agente.

Arquitectura:
  Usuario → Gradio UI → Groq API (primario) → KB TF-IDF (fallback)

Despliegue:
  OCI Compute + Docker + Nginx reverse proxy

Variables de entorno:
  GROQ_API_KEY   — clave de Groq (gratis: console.groq.com/keys)
  GROQ_MODEL     — modelo LLM (default: llama-3.3-70b-versatile)
  PORT           — puerto (default: 7860)
"""

import os, re, json, urllib.request
from typing import Optional

# ─── Config ──────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
KB_PATH      = os.path.join(os.path.dirname(__file__), "data", "kb_chunks.json")

# ─── Knowledge Base (TF-IDF local) ───────────────────────────────────
def load_kb() -> list:
    if not os.path.exists(KB_PATH):
        return []
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

KB_CHUNKS = load_kb()

def search_kb(query: str, top_k: int = 4) -> list:
    if not KB_CHUNKS or not query:
        return []
    def tokenize(text: str) -> list:
        return re.findall(r"[a-záéíóúüñ0-9]{2,}", text.lower())
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    scored = []
    for chunk in KB_CHUNKS:
        chunk_tokens = tokenize(chunk["content"])
        matches = sum(1 for qt in query_tokens if qt in chunk_tokens)
        score = matches / max(1, len(chunk_tokens) ** 0.5)
        if score > 0.01:
            scored.append({**chunk, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

# ─── Respuestas directas (conversación natural) ──────────────────────
def direct_response(query: str) -> Optional[str]:
    q = query.lower().strip().rstrip("?!¿¡").replace("  ", " ")

    if any(w in q for w in ["hola", "buen dia", "buenas", "que tal", "hey", "hi", "saludos"]):
        return "¡Hola! 👋 Soy **medicalMen** 🩺, el asistente virtual de Medicamentum360. Pregúntame sobre cursos, precios, reembolsos, cómo vender tus cursos o capacitación corporativa. ¿En qué te ayudo?"

    if any(w in q for w in ["como estas", "como esta", "como vas", "como te va", "todo bien", "que tal"]):
        return "¡Muy bien, gracias! 😊 Estoy aquí 24/7 listo para resolver tus dudas sobre Medicamentum360. ¿En qué puedo ayudarte?"

    if any(w in q for w in ["quien eres", "que eres", "quien sos", "como te llamas", "que haces"]):
        return "Soy **medicalMen** 🩺, el agente de inteligencia artificial de **Medicamentum360**, la plataforma SaaS de e-learning médico en Colombia. Uso **Groq (Llama 3.3 70B)** y una base de conocimiento de más de 1,500 líneas de documentación oficial para responder tus preguntas con precisión. ¿Qué necesitas saber?"

    if any(w in q for w in ["gracias", "te agradezco", "mil gracias"]):
        return "¡De nada! 😊 Es un placer ayudarte. ¿Algo más sobre Medicamentum360 en lo que pueda asistirte?"

    if any(w in q for w in ["adios", "chao", "hasta luego", "nos vemos", "bye"]):
        return "¡Hasta pronto! 🩺 Vuelve cuando necesites información sobre la plataforma. Estaré aquí."

    if any(w in q for w in ["que puedes hacer", "que haces", "ayuda", "help", "sobre que", "puedo preguntar", "que me puedes decir", "de que temas", "capacidades", "funciones"]):
        return """Puedo ayudarte con **todo esto** sobre Medicamentum360:

📚 **Cursos y marketplace** — catálogo, cómo funcionan
💰 **Precios y pagos** — métodos de pago, costos
🏥 **Capacitación corporativa** — comprar cursos para empleados de tu hospital
👨‍🏫 **Ser instructor (vendor)** — cómo vender tus propios cursos en la plataforma
🔄 **Reembolsos** — política de devolución
🔒 **Privacidad** — cómo protegemos tus datos (Ley 1581 Colombia)
📧 **Soporte técnico** — canales de ayuda

¡Pregúntame lo que quieras! 🩺"""

    return None

# ─── Groq API (Llama 3.3 70B — gratis, ~300 tok/s) ─────────────────
SYSTEM_PROMPT = """Eres medicalMen, el asistente virtual de Medicamentum360, una plataforma SaaS de e-learning médico que opera en Colombia. Tu función es ayudar a usuarios (médicos, enfermeros, administradores de hospitales, instructores) a entender cómo funciona la plataforma.

REGLAS:
1. Responde en español colombiano con tono profesional pero cálido y cercano.
2. Si el usuario te saluda o hace conversación casual, responde naturalmente.
3. Si la pregunta es sobre la plataforma, usa el CONTEXTO proporcionado.
4. Siempre cita la fuente si usas información del contexto.
5. Si la respuesta NO está en el contexto, sé honesto y sugiere contactar soporte.
6. NUNCA inventes datos, precios, políticas o funcionalidades que no estén en el contexto.
7. Para preguntas médicas clínicas, aclara que eres un asistente de plataforma, no un médico.
8. Mantén respuestas concisas pero completas (3-5 párrafos máximo).
9. Usa emojis con moderación para hacer la conversación más amigable.
10. Si te preguntan algo que ya respondiste, puedes referenciar tu respuesta anterior."""

def call_groq(query: str, context: str = "") -> Optional[str]:
    if not GROQ_API_KEY:
        return None
    prompt = f"CONTEXTO DE LA PLATAFORMA:\n{context}\n\nPREGUNTA: {query}" if context else query
    try:
        body = json.dumps({
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 600,
            "temperature": 0.4,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception as e:
        print(f"[Groq] Error: {e}")
        return None

# ─── Chat principal ──────────────────────────────────────────────────
def chat(message: str, history: list) -> str:
    query = message.strip()
    if not query:
        return ""

    direct = direct_response(query)
    if direct:
        return direct

    results = search_kb(query, 4)
    context = "\n\n".join(f"[Fuente: {r['source']}]\n{r['content']}" for r in results)

    if GROQ_API_KEY:
        answer = call_groq(query, context)
        if answer:
            return answer

    if results:
        answer = results[0]["content"].strip()[:1500]
        return f"{answer}\n\n📄 *Fuente: {results[0]['source']}*"

    return "No encontré esa información en mi base de conocimiento. 📝 Visita **medicamentum360.com** o contacta a **soporte@medicamentum360.com** para ayuda personalizada. ¿Hay algo más en lo que pueda ayudarte?"

# ─── UI (Gradio + tema Medicamentum360 oscuro) ───────────────────────
CUSTOM_CSS = """
/* === Medicamentum360 Dark Theme (identical to ChatWidget) === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', system-ui, -apple-system, sans-serif !important; }

body, .gradio-container, .contain, .app {
  background: linear-gradient(135deg, #0d0221, #1a0533, #2d0b4e) !important;
  min-height: 100vh !important;
  color: #e9d5ff !important;
}

/* Header */
h1, h2, h3, h4, label, .block-label {
  color: #e9d5ff !important;
  font-weight: 600 !important;
}

/* Chat container */
.chatbot, .message-wrap, .bubble-wrap {
  background: transparent !important;
  border: none !important;
}

/* User bubble (violet) */
.bubble-wrap .user, .message.user .bubble, [class*="user"] .bubble {
  background: #7c3aed !important;
  color: white !important;
  border-radius: 16px 16px 4px 16px !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  max-width: 85% !important;
}

/* Bot bubble (glass) */
.bubble-wrap .bot, .message.bot .bubble, [class*="bot"] .bubble, [class*="assistant"] .bubble {
  background: rgba(255,255,255,0.08) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  color: #e5e7eb !important;
  border-radius: 16px 16px 16px 4px !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  max-width: 85% !important;
}

/* Input */
textarea, input[type="text"], .gr-textbox textarea, .gr-textbox input, .textbox textarea {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 14px !important;
  color: #e5e7eb !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  outline: none !important;
  transition: border-color 0.2s ease !important;
}
textarea:focus, input:focus {
  border-color: #7c3aed !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}
textarea::placeholder, input::placeholder {
  color: #6b7280 !important;
}

/* Send button */
.gr-button-primary, button.primary, .btn-primary, .send-btn {
  background: #7c3aed !important;
  border: none !important;
  border-radius: 12px !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 10px 18px !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
}
.gr-button-primary:hover, button.primary:hover {
  background: #6d28d9 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(124,58,237,0.4) !important;
}

/* Examples */
.examples, .gr-examples {
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 12px !important;
  padding: 12px !important;
  background: rgba(255,255,255,0.02) !important;
}
.example, .gr-examples .example {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 8px !important;
  color: #a78bfa !important;
  padding: 6px 12px !important;
  font-size: 13px !important;
  transition: all 0.2s ease !important;
}
.example:hover, .gr-examples .example:hover {
  background: rgba(124,58,237,0.15) !important;
  border-color: #7c3aed !important;
  color: #c4b5fd !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px !important; }
::-webkit-scrollbar-track { background: transparent !important; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1) !important; border-radius: 3px !important; }

/* Chat area */
.chatbot, .chatbot > div {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 16px !important;
}

/* Hide Gradio footer/branding */
footer, .footer, .dark .footer, #footer, .gradio-footer {
  display: none !important;
  opacity: 0 !important;
  height: 0 !important;
  visibility: hidden !important;
}

/* Rows */
.row, .form {
  background: transparent !important;
  border: none !important;
}

/* Panel */
.panel, .prose {
  background: transparent !important;
}

/* Hide built-with-gradio */
.contain > div:last-child {
  display: none !important;
}
"""

EXAMPLES = [
    "¿Qué es Medicamentum360 y qué servicios ofrece?",
    "¿Cómo se paga en la plataforma y cuánto cuesta?",
    "Soy administrador de un hospital, ¿cómo compro cursos para mis empleados?",
    "Compré un curso pero no es lo que esperaba, ¿puedo pedir reembolso?",
    "Quiero vender mis cursos de farmacología, ¿cómo me convierto en instructor?",
    "¿Mis datos personales están seguros en la plataforma?",
]

def build_ui():
    import gradio as gr

    with gr.Blocks(title="medicalMen — Medicamentum360", css=CUSTOM_CSS) as demo:
        gr.HTML("""
        <div style="text-align:center;padding:24px 0 8px">
          <h1 style="font-size:2.2rem;margin:0">🩺 medicalMen</h1>
          <p style="color:#a78bfa;font-size:0.95rem;margin:4px 0 16px">
            Asistente IA de <strong>Medicamentum360</strong> — Plataforma SaaS de e-learning médico
          </p>
        </div>
        """)

        chatbot = gr.Chatbot(
            value=[{
                "role": "assistant",
                "content": "¡Hola! 👋 Soy **medicalMen** 🩺<br><br>Tu asistente virtual de **Medicamentum360**, la plataforma de formación médica. Pregúntame sobre cursos, precios, reembolsos, cómo vender tus cursos o capacitación corporativa.<br><br>¿En qué te ayudo hoy?",
            }],
            label="",
            height=440,
            show_label=False,
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="💬 Escribe tu consulta sobre Medicamentum360...",
                show_label=False,
                container=False,
                scale=9,
            )
            send = gr.Button("Enviar", variant="primary", scale=1, size="sm")

        gr.Examples(EXAMPLES, inputs=msg, label="💡 Ejemplos de preguntas que puedo responder")

        gr.HTML("""
        <div style="text-align:center;margin-top:16px;padding:12px;color:#a78bfa;font-size:0.8rem;
                    border-top:1px solid rgba(255,255,255,0.06)">
          <strong>medicalMen 🩺</strong> · Groq + Llama 3.3 70B · 237 documentos · 1,525 líneas de KB ·
          <a href="https://github.com/willestingbio/med360-agent" style="color:#6366f1" target="_blank">GitHub</a> ·
          Challenge Alura Agente (ONE + Alura Latam)
        </div>
        """)

        def respond(message, history):
            return history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": chat(message, history)},
            ]

        msg.submit(respond, [msg, chatbot], [chatbot]).then(lambda: "", None, [msg])
        send.click(respond, [msg, chatbot], [chatbot]).then(lambda: "", None, [msg])

    return demo

if __name__ == "__main__":
    print("🩺 medicalMen iniciando...")
    print(f"   KB chunks: {len(KB_CHUNKS)}")
    print(f"   Groq key: {'configurada' if GROQ_API_KEY else 'NO configurada'}")
    print(f"   Modelo: {GROQ_MODEL}")
    demo = build_ui()
    port = int(os.getenv("PORT", "7860"))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
