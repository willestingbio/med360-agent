"""
medicalMen — Agente IA de Medicamentum360
==========================================
Chatbot con RAG para Challenge Alura Agente (ONE + Alura Latam).

Stack: Streamlit + Groq (Llama 3.3 70B) + TF-IDF local
Deploy: OCI Free Tier + Nginx

Uso:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os, re, json, urllib.request, streamlit as st
from typing import Optional

# ─── Config ──────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
KB_PATH      = os.path.join(os.path.dirname(__file__), "data", "kb_chunks.json")

st.set_page_config(page_title="medicalMen — Medicamentum360", page_icon="🩺")

# ─── CSS ─────────────────────────────────────────────────────────────
# Minimal CSS — solo colores, sin ocultar nada
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0d0221, #1a0533, #2d0b4e); }
h1 { background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.4rem; text-align: center; }
.stChatMessage [data-testid="stChatMessageContent"] { border-radius: 16px; padding: 14px 18px; }
section[data-testid="stSidebar"] { background: rgba(255,255,255,0.03); }
</style>
""", unsafe_allow_html=True)

# ─── Knowledge Base ──────────────────────────────────────────────────
@st.cache_resource
def load_kb():
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

# ─── Groq ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres medicalMen, asistente virtual de Medicamentum360, plataforma SaaS de e-learning médico en Colombia. Reglas:
1. Responde en español colombiano, tono profesional pero cálido.
2. Saludos y conversación casual: responde natural y brevemente.
3. Preguntas sobre la plataforma: usa el CONTEXTO proporcionado.
4. Cita la fuente si usas información del contexto.
5. Si no está en el contexto, sé honesto.
6. NUNCA inventes datos, precios o políticas.
7. Para preguntas médicas, aclara que eres asistente de plataforma.
8. Respuestas concisas (3-5 párrafos max)."""

def call_groq(query: str, context: str = "") -> Optional[str]:
    if not GROQ_API_KEY:
        return None
    prompt = f"CONTEXTO:\n{context}\n\nPREGUNTA: {query}" if context else query
    try:
        body = json.dumps({
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500, "temperature": 0.4,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception as e:
        st.warning(f"Error Groq: {e}")
        return None

# ─── Respuesta ───────────────────────────────────────────────────────
def get_response(query: str) -> str:
    q = query.lower().strip().rstrip("?!¿¡").replace("  ", " ")

    if any(w in q for w in ["hola", "buen dia", "buenas", "que tal", "hey", "hi", "saludos"]):
        return "¡Hola! 👋 Soy **medicalMen** 🩺, el asistente virtual de **Medicamentum360**, la plataforma SaaS de e-learning médico en Colombia. Pregúntame sobre cursos, precios, reembolsos, cómo vender tus cursos o capacitación corporativa. ¿En qué te ayudo?"

    if any(w in q for w in ["como estas", "como esta", "como vas", "como te va", "todo bien"]):
        return "¡Muy bien, gracias! 😊 Estoy aquí listo para ayudarte con cualquier duda sobre Medicamentum360. ¿En qué puedo ayudarte?"

    if any(w in q for w in ["quien eres", "que eres", "como te llamas"]):
        return "Soy **medicalMen** 🩺, el agente de IA de **Medicamentum360**. Uso **Groq (Llama 3.3 70B)** y una base de conocimiento de más de 1,500 líneas de documentación oficial. ¿Qué necesitas saber?"

    if any(w in q for w in ["gracias", "te agradezco"]):
        return "¡De nada! 😊 ¿Algo más en lo que pueda ayudarte?"

    if any(w in q for w in ["adios", "chao", "hasta luego", "bye"]):
        return "¡Hasta pronto! 🩺 Vuelve cuando necesites información sobre la plataforma."

    if any(w in q for w in ["que puedes hacer", "ayuda", "help", "sobre que", "puedo preguntar", "capacidades"]):
        return "Puedo ayudarte con:\n\n📚 **Cursos y marketplace**\n💰 **Precios, pagos, reembolsos**\n🏥 **Capacitación corporativa** (comprar cursos para tu hospital)\n👨‍🏫 **Ser instructor/vendor** (vender tus cursos)\n🔒 **Privacidad y seguridad**\n\n¡Pregúntame lo que quieras! 🩺"

    results = search_kb(query, 4)
    context = "\n\n".join(f"[{r['source']}]\n{r['content']}" for r in results)

    answer = call_groq(query, context)
    if answer:
        return answer

    if results:
        a = results[0]["content"].strip()[:1500]
        return f"{a}\n\n📄 *{results[0]['source']}*"

    return "No encontré esa información en mi base de conocimiento. 📝 Visita **medicamentum360.com** o contacta a **soporte@medicamentum360.com**. ¿Hay algo más en lo que pueda ayudarte?"

# ─── UI ───────────────────────────────────────────────────────────────
st.markdown("<h1>🩺 medicalMen</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#a78bfa;margin-bottom:24px'>"
    "Asistente IA de <strong>Medicamentum360</strong> · Groq + Llama 3.3 70B · Challenge Alura Agente</p>",
    unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.metric("Modelo", "Llama 3.3 70B")
    st.metric("KB chunks", len(KB_CHUNKS))
    st.metric("API Groq", "✅ Conectada" if GROQ_API_KEY else "❌ Sin key")
    st.markdown("---")
    st.markdown("### 💡 Ejemplos")
    st.markdown("- ¿Qué es Medicamentum360?")
    st.markdown("- ¿Cómo se paga en la plataforma?")
    st.markdown("- ¿Cómo compro cursos para mi hospital?")
    st.markdown("- ¿Puedo pedir reembolso?")
    st.markdown("- ¿Cómo vender mis cursos?")
    st.markdown("---")
    st.markdown("[GitHub](https://github.com/willestingbio/med360-agent)")
    st.markdown("Challenge Alura Agente · ONE + Alura Latam")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! 👋 Soy **medicalMen** 🩺, tu asistente virtual de **Medicamentum360**. Pregúntame sobre cursos, precios, reembolsos, cómo vender tus cursos o capacitación corporativa. ¿En qué te ayudo hoy?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🩺" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("💬 Escribe tu consulta sobre Medicamentum360..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("Pensando..."):
            response = get_response(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
