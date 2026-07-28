"""
medicalMen — Agente IA de Medicamentum360
==========================================
Chatbot con RAG para el Challenge Alura Agente (ONE + Alura Latam).

Usa Groq (Llama 3.3 70B, gratuito) + Gradio para interfaz web pública.
Base de conocimiento de 1,525 líneas de docs de la plataforma.

Ejecución local:
    pip install -r requirements.txt
    GROQ_API_KEY=tu_key python app.py

Docker:
    docker build -t medicalmen .
    docker run -p 7860:7860 -e GROQ_API_KEY=tu_key medicalmen

Despliegue OCI / Cloud Run:
    gcloud run deploy medicalmen --source . --set-env-vars=GROQ_API_KEY=tu_key
"""

import os
import re
import json
import urllib.request
from typing import Optional

# ─── Config ──────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
KB_PATH = os.path.join(os.path.dirname(__file__), "data", "kb_chunks.json")

# ─── Knowledge Base ──────────────────────────────────────────────────
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

# ─── Respuestas directas ─────────────────────────────────────────────
def direct_response(query: str) -> Optional[str]:
    q = query.lower().strip().rstrip("?!¿¡").replace("  ", " ")

    greetings = ["hola", "hola como estas", "buenos dias", "buenas tardes", "buenas noches", "hey", "hi"]
    if q in greetings:
        return (
            "¡Hola! 👋 Soy **medicalMen** 🩺, el asistente virtual de Medicamentum360. "
            "Puedo ayudarte con información sobre cursos médicos, marketplace, precios, "
            "reembolsos, cómo vender tus cursos y soporte técnico. ¿En qué te puedo ayudar?"
        )

    identity = ["quien eres", "que eres", "quien sos", "como te llamas"]
    if q in identity:
        return (
            "Soy **medicalMen** 🩺, el asistente virtual con IA de Medicamentum360. "
            "Mi función es ayudarte con información sobre la plataforma: cursos médicos, "
            "marketplace, precios, capacitación corporativa, cómo crear y vender cursos, "
            "privacidad y soporte técnico. Uso Groq (Llama 3.3 70B) para darte "
            "respuestas precisas basadas en documentación oficial."
        )

    if q in ["gracias", "muchas gracias"]:
        return "¡De nada! 😊 ¿Hay algo más en lo que pueda ayudarte?"

    if q in ["adios", "chao", "hasta luego", "nos vemos"]:
        return "¡Hasta pronto! 🩺 No dudes en volver si tienes más preguntas."

    if q in ["que puedes hacer", "que haces", "ayuda", "help"]:
        return (
            "Puedo ayudarte con:\n📚 Cursos y marketplace\n💰 Precios y reembolsos\n"
            "🏥 Capacitación corporativa\n👨‍🏫 Cómo convertirte en vendedor (vendor)\n"
            "🔒 Privacidad y datos\n❓ Soporte técnico\n\n¡Pregúntame lo que necesites! 🩺"
        )

    return None

# ─── Groq (Llama 3.3 70B) ───────────────────────────────────────────
SYSTEM_PROMPT = (
    "Eres medicalMen, el asistente virtual de Medicamentum360, una plataforma SaaS de "
    "e-learning médico en Colombia. Responde en español colombiano con tono profesional "
    "pero cercano y cálido. Cita la fuente si usas información del contexto. "
    "Si no encuentras la respuesta en el contexto, sé honesto y sugiere contactar soporte. "
    "NUNCA inventes información. Para preguntas médicas clínicas, aclara que eres un "
    "asistente de plataforma, no un médico."
)

def call_groq(query: str, context: str = "") -> Optional[str]:
    if not GROQ_API_KEY:
        return None

    prompt = context if context else query
    if context:
        prompt = f"CONTEXTO DE LA PLATAFORMA (basa tu respuesta en esto):\n{context}\n\nPREGUNTA: {query}"

    try:
        body = json.dumps({
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500,
            "temperature": 0.4,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
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

    # 1. Saludos e identidad
    direct = direct_response(query)
    if direct:
        return direct

    # 2. Buscar en KB
    results = search_kb(query, 4)
    context = "\n\n".join(
        f"[Fuente: {r['source']}]\n{r['content']}" for r in results
    )

    # 3. Groq (primario, gratuito)
    if GROQ_API_KEY:
        answer = call_groq(query, context)
        if answer:
            return answer

    # 4. Fallback: KB directa
    if results:
        answer = results[0]["content"].strip()[:1500]
        return f"{answer}\n\n📄 *Fuente: {results[0]['source']}*"

    # 5. Sin respuesta
    return (
        "No encontré información sobre eso. Te sugiero:\n\n"
        "📝 Web: https://medicamentum360.com\n"
        "💬 Soporte: /soporte\n📧 soporte@medicamentum360.com\n\n"
        "¿Algo más en lo que pueda ayudarte?"
    )

# ─── Gradio UI ───────────────────────────────────────────────────────
EXAMPLES = [
    "¿Qué es Medicamentum360 y qué servicios ofrece?",
    "¿Cómo se paga en la plataforma?",
    "Soy administrador de un hospital, ¿cómo compro cursos para mis empleados?",
    "¿Puedo pedir reembolso si no me gustó el curso?",
    "Quiero vender mis cursos, ¿cómo empiezo?",
]

def build_ui():
    import gradio as gr

    with gr.Blocks(
        title="medicalMen — Medicamentum360",
        theme=gr.themes.Soft(primary_hue="violet"),
        css="footer { display: none !important; }",
    ) as demo:
        gr.Markdown(
            "# 🩺 medicalMen\n"
            "### Asistente IA de Medicamentum360\n"
            "[GitHub](https://github.com/willestingbio/med360-agent) · "
            "Groq + Llama 3.3 70B · RAG con TF‑IDF · Challenge Alura Agente"
        )

        chatbot = gr.Chatbot(
            value=[(
                None,
                "¡Hola! 👋 Soy **medicalMen** 🩺, tu asistente virtual de "
                "Medicamentum360. Pregúntame sobre cursos, precios, reembolsos, "
                "capacitación corporativa o cómo vender tus cursos. ¿En qué te ayudo?",
            )],
            label="Chat",
            height=450,
            avatar_images=(None, "🩺"),
        )

        msg = gr.Textbox(
            placeholder="Escribe tu consulta sobre Medicamentum360...",
            label="Tu pregunta",
            container=False,
            scale=7,
        )
        clear = gr.ClearButton([msg, chatbot], value="Limpiar chat")

        gr.Examples(EXAMPLES, inputs=msg, label="Ejemplos de preguntas")

        gr.Markdown(
            "---\n"
            "*medicalMen 🩺 — Groq + Llama 3.3 70B · KB: 237 chunks · "
            "Challenge Alura Agente (ONE + Alura Latam)*"
        )

        msg.submit(chat, [msg, chatbot], [chatbot]).then(lambda: "", None, [msg])

    return demo


if __name__ == "__main__":
    print("🩺 medicalMen iniciando...")
    print(f"   KB chunks: {len(KB_CHUNKS)}")
    print(f"   Groq key: {'configurada' if GROQ_API_KEY else 'NO configurada'}")
    print(f"   Modelo: {GROQ_MODEL}")
    demo = build_ui()
    port = int(os.getenv("PORT", "7860"))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
