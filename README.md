# 🩺 Dr. Medici — Agente IA de Medicamentum360

[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![n8n](https://img.shields.io/badge/n8n-✓-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-✓-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC382D?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![RAG](https://img.shields.io/badge/RAG-Retrieval_Augmented_Generation-8A2BE2)](https://en.wikipedia.org/wiki/Prompt_engineering#Retrieval-augmented_generation)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![OCI](https://img.shields.io/badge/Deploy-OCI-F80000?logo=oracle&logoColor=white)](./docs/GUIA_DESPLIEGUE_OCI.md)
[![Repo](https://img.shields.io/badge/GitHub-willestingbio%2Fmed360--agent-181717?logo=github)](https://github.com/willestingbio/med360-agent)

**Asistente virtual con IA para la plataforma de e-learning médico Medicamentum360.**

Dr. Medici es un agente de inteligencia artificial que responde preguntas sobre la plataforma Medicamentum360 usando **RAG (Retrieval-Augmented Generation)** con una base de conocimiento de más de 1,500 líneas de documentación oficial. El agente está orquestado con **n8n**, usa búsqueda semántica vectorial con **Qdrant** y **embeddings multilingües**, y se integra como **widget de chat** embebible en cualquier página web.

---

## 📐 Arquitectura

```
┌──────────────────────────────────────────────────────────┐
│                    👤 Usuario Final                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Medicamentum360 (Next.js)                         │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  💬 Widget @n8n/chat (embed)                  │  │  │
│  │  │  "¿Cómo creo un curso en el marketplace?"     │  │  │
│  │  └──────────────────┬───────────────────────────┘  │  │
│  └─────────────────────┼──────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────┘
                         │ HTTPS POST /webhook/dr-medici-chat
┌────────────────────────▼─────────────────────────────────┐
│                    ☁️ Oracle Cloud (OCI)                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │                 🟢 Nginx Reverse Proxy               │  │
│  │            (SSL Let's Encrypt + Rate Limiting)       │  │
│  └───┬────────────────────────────────────┬───────────┘  │
│      │                                    │               │
│  ┌───▼──────────────┐      ┌──────────────▼───────────┐  │
│  │  🔧 n8n (Docker)  │      │  🧠 Knowledge API        │  │
│  │                  │      │  (FastAPI + Python)       │  │
│  │  ┌─────────────┐ │      │                          │  │
│  │  │ Webhook      │ │      │   POST /search            │  │
│  │  │   ↓          │ │      │     ↓                     │  │
│  │  │ AI Agent     │─┼──────┼─→ Embedding query         │  │
│  │  │   ├─ Tool:   │ │      │     ↓                     │  │
│  │  │   │  buscar_ │ │      │  Search Qdrant            │  │
│  │  │   │  base_   │ │      │     ↓                     │  │
│  │  │   │  conoci- │ │      │  Return top-K chunks      │  │
│  │  │   │  miento  │ │      │                          │  │
│  │  │   ↓          │ │      └──────────────┬───────────┘  │
│  │  │ Response     │ │                     │               │
│  │  └─────────────┘ │      ┌──────────────▼───────────┐  │
│  └──────────────────┘      │  🔴 Qdrant (Vector DB)    │  │
│                            │  Collection:              │  │
│                            │  med360_knowledge         │  │
│                            │  384-dim vectors          │  │
│                            │  ~200 chunks              │  │
│                            └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Flujo de una consulta

1. **Usuario** escribe una pregunta en el widget de chat embebido en Medicamentum360.
2. **@n8n/chat SDK** envía la pregunta vía POST al webhook de n8n.
3. **n8n AI Agent** recibe la pregunta y decide usar la herramienta `buscar_base_conocimiento`.
4. La herramienta hace un **HTTP Request** a la Knowledge API (`POST /search`) con la consulta del usuario.
5. La **Knowledge API** genera embeddings de la consulta usando `paraphrase-multilingual-MiniLM-L12-v2` y busca en **Qdrant** los 5 chunks más relevantes por similitud coseno.
6. Los resultados se formatean y se devuelven al AI Agent como contexto.
7. El **LLM** (OpenAI GPT-4o / Google Gemini) genera una respuesta precisa basada **únicamente** en el contexto recuperado + el system prompt de Dr. Medici.
8. La respuesta se envía de vuelta al widget y se muestra al usuario, **citando la fuente**.

---

## 🛠️ Tecnologías

| Componente | Tecnología | Justificación |
|---|---|---|
| **Orquestador IA** | n8n (Docker) | Flujos visuales, webhooks nativos, AI Agent node, chat widget SDK integrado |
| **LLM** | OpenAI GPT-4o / Google Gemini | Respuestas de alta calidad en español, comprensión contextual |
| **Embeddings** | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Modelo multilingüe ligero (120 MB), optimizado para español, 384 dimensiones |
| **Vector DB** | Qdrant (Docker) | Búsqueda por similitud coseno, API REST, persistente, rápido |
| **API de búsqueda** | FastAPI + Python 3.12 | Endpoint REST para n8n, CORS habilitado, documentación Swagger automática |
| **Chunking** | LangChain `RecursiveCharacterTextSplitter` | División inteligente de documentos por secciones Markdown |
| **Widget** | @n8n/chat SDK (CDN) | Burbuja de chat flotante, personalizable, soporte i18n español |
| **Proxy inverso** | Nginx (Docker) | Terminación SSL, rate limiting, proxy a n8n y API |
| **SSL** | Let's Encrypt + Certbot | Certificados gratuitos, renovación automática |
| **Contenedores** | Docker Compose | Orquestación de 5 servicios, volúmenes persistentes, healthchecks |
| **Cloud** | Oracle Cloud Infrastructure (OCI) | Compute Free Tier, IP pública, firewall configurable |

---

## 📁 Estructura del proyecto

```
med360-agent/
├── README.md                          # ← Este archivo
├── LICENSE                            # MIT
├── .env.example                       # Template de variables de entorno
├── .gitignore
├── .dockerignore
├── docker-compose.yml                 # Stack: n8n + Qdrant + API + Nginx + Certbot
├── docker-compose.prod.yml            # Overrides de producción
├── Dockerfile.api                     # Imagen de la Knowledge API
│
├── knowledge-base/                    # 📚 Documentos fuente (1,525 líneas)
│   ├── conocimiento-producto.md       #     Arquitectura, roles, marketplace, Course Builder
│   ├── faq-soporte.md                 #     256 líneas de FAQ categorizadas
│   ├── politica-privacidad.md         #     Ley 1581/2012 Colombia
│   ├── planes-precios.md              #     Precios, comisiones, payouts
│   └── terminos-uso.md                 #     Términos legales completos
│
├── src/                               # 🐍 Python — Knowledge API
│   ├── config.py                      #     Configuración central
│   ├── ingest.py                      #     Chunking + embeddings → Qdrant
│   ├── api.py                         #     FastAPI REST API (/search, /health)
│   ├── prompts.py                     #     System prompts y personalidad del agente
│   └── requirements.txt               #     Dependencias Python
│
├── n8n-workflows/                     # ⚡ Workflows de n8n
│   ├── dr-medici-agent.json           #     Workflow principal del agente
│   └── knowledge-ingestion.json       #     Workflow de reindexación programada
│
├── widget/                            # 💬 Widget de chat
│   ├── dr-medici-demo.html            #     Página demo con el widget
│   └── embed-snippet.js               #     Snippet para embeber en Next.js
│
├── nginx/                             # 🔀 Reverse proxy
│   ├── nginx.conf                     #     Configuración principal
│   └── conf.d/
│       └── med360-agent.conf          #     Virtual host
│
├── scripts/
│   ├── setup.sh                       #     Instalación one-command
│   └── entrypoint.sh                  #     Entrypoint del contenedor API
│
├── docs/
│   └── GUIA_DESPLIEGUE_OCI.md         #     Guía completa de despliegue en OCI
│
├── evidencias/                        #     Capturas de pantalla
│
└── data/                              #     Datos generados en runtime
    └── .gitkeep
```

---

## 💬 Ejemplos de preguntas y respuestas

### 1. Información general de la plataforma

> **Usuario:** *"¿Qué es Medicamentum360 y qué servicios ofrece?"*
>
> **Dr. Medici:** *"Medicamentum360 es una plataforma SaaS de e-learning y marketplace para el sector salud en Colombia. Permite a hospitales, clínicas y profesionales de la salud comprar, crear y vender cursos médicos, experiencias de realidad virtual (VR) y automatizaciones clínicas. Sus pilares son: Marketplace centralizado de formación médica, Course Builder propio, Marketplace multi-vendor para instructores externos, Capacitación corporativa (B2B) e Integración con Moodle. 🩺 *(Fuente: conocimiento-producto.md)*"

### 2. Precios y pagos

> **Usuario:** *"¿Cómo se paga en la plataforma y cuánto cuesta?"*
>
> **Dr. Medici:** *"Medicamentum360 opera con un modelo **transaccional**, no por suscripción. Cada curso o experiencia VR se compra individualmente en el marketplace. Los pagos se procesan a través de Wompi, que acepta tarjetas de crédito/débito (Visa, Mastercard, American Express), PSE, Nequi y Daviplata. El IVA es del 19% y se desglosa en el checkout. Si eres vendor, la comisión estándar es del 20% por venta y recibes pagos mensuales vía transferencia bancaria. 💰 *(Fuente: planes-precios.md)*"

### 3. Capacitación corporativa

> **Usuario:** *"Soy administrador de un hospital, ¿cómo compro cursos para mis empleados?"*
>
> **Dr. Medici:** *"Como hospital_admin, puedes comprar cupos en lote para tu organización. El flujo es: 1. En el detalle de un curso, activa el toggle 'Comprar para mi organización', 2. Selecciona la cantidad de empleados, 3. El precio total = precio unitario × cantidad + IVA, 4. Completa el pago vía Wompi, 5. Desde /org/employees, asigna los cupos a cada empleado usando el botón 'Asignar curso'. Los cupos no asignados se muestran en un banner persistente hasta que los uses. 🏥 *(Fuente: conocimiento-producto.md)*"

### 4. Reembolsos

> **Usuario:** *"Compré un curso pero no es lo que esperaba, ¿puedo pedir reembolso?"*
>
> **Dr. Medici:** *"Sí, tienes derecho a solicitar reembolso dentro de los **7 días** siguientes a la compra, siempre que hayas completado **menos del 20%** del curso. Para solicitarlo: 1. Ve a /orders (historial de compras), 2. Busca la orden y haz clic en 'Solicitar reembolso', 3. Selecciona el motivo y envía la solicitud. El equipo de Medicamentum360 la revisará y, si cumple los criterios, procesará el reembolso vía Wompi. Para compras corporativas, solo el hospital_admin puede solicitarlo. *(Fuente: faq-soporte.md)*"

### 5. Cómo vender cursos

> **Usuario:** *"Quiero vender mis cursos de farmacología en la plataforma, ¿cómo empiezo?"*
>
> **Dr. Medici:** *"¡Excelente! Para convertirte en vendor: 1. Regístrate como usuario normal si aún no tienes cuenta, 2. Ve a /vender y completa el registro como creador (nombre público, bio), 3. Completa tus datos fiscales (NIT o CC) y bancarios para recibir pagos, 4. El equipo revisa tu perfil (máx 48h), 5. Una vez aprobado, accede a /instructor para crear tu primer curso. Recibirás el 80% de cada venta (comisión del 20%). Los pagos son mensuales. 👨‍🏫 *(Fuente: conocimiento-producto.md)*"

### 6. Privacidad de datos

> **Usuario:** *"¿Mis datos están seguros? ¿Cumplen con la ley colombiana?"*
>
> **Dr. Medici:** *"Sí, Medicamentum360 cumple con la **Ley 1581 de 2012** (Habeas Data) de Colombia. Tus datos personales se tratan conforme a nuestra Política de Privacidad. Implementamos: cifrado AES-256-GCM para datos bancarios de vendors, TLS 1.3 para toda comunicación, Row Level Security (RLS) en Postgres que aísla los datos entre organizaciones, autenticación con 2FA opcional, y URLs firmadas con expiración para documentos sensibles. Puedes ejercer tus derechos de acceso, rectificación y supresión desde /configuracion. 🔒 *(Fuente: politica-privacidad.md)*"

### 7. Pregunta fuera de alcance + anti-alucinación

> **Usuario:** *"¿Cuál es el tratamiento para la hipertensión arterial?"*
>
> **Dr. Medici:** *"Como asistente de IA de Medicamentum360, mi especialidad es ayudarte con información sobre la plataforma: cursos, marketplace, precios, capacitación corporativa y soporte técnico. No estoy capacitado para dar consejos médicos ni diagnósticos. Para información sobre tratamientos médicos, te recomiendo consultar a un profesional de la salud o revisar guías clínicas oficiales. ¿Hay algo sobre Medicamentum360 en lo que pueda ayudarte? 🩺"*

---

## 🚀 Instalación y ejecución local

### Requisitos

- Docker y Docker Compose v2
- Git
- Clave API de un proveedor LLM (OpenAI o Google Gemini)
- 4 GB RAM disponibles (para el modelo de embeddings)

### Quickstart (3 pasos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env → pegar tu OPENAI_API_KEY o GOOGLE_API_KEY

# 3. Levantar todos los servicios
chmod +x scripts/setup.sh scripts/entrypoint.sh
docker compose up -d
```

### Verificar instalación

```bash
# Ver servicios
docker compose ps
# Deberías ver: n8n, qdrant, knowledge-api, nginx → Up

# Verificar health de la API
curl http://localhost:8001/health
# → {"status":"ok","collection":"med360_knowledge","vectors":200}

# Verificar búsqueda
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Cómo funciona el marketplace"}'
```

### Configurar n8n

1. Abre **http://localhost:5678** y crea cuenta de administrador.
2. Ve a **Settings → Community Nodes** → instala `@n8n/n8n-nodes-langchain`.
3. Importa el workflow: **Workflows → Import from File** → `n8n-workflows/dr-medici-agent.json`.
4. Configura el nodo **AI Agent** con tu proveedor LLM y API key.
5. **Activa** el workflow.
6. Abre **http://localhost/widget** y prueba el chat.

---

## 🔌 Integración con Medicamentum360 (Next.js)

Agrega al `layout.tsx` de tu app Next.js:

```tsx
import Script from 'next/script';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="antialiased">
        {children}

        {/* CSS del widget de chat */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css"
        />

        {/* SDK de n8n chat */}
        <Script
          src="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js"
          strategy="afterInteractive"
        />

        {/* Configuración: URL del webhook de n8n */}
        <Script id="dr-medici-config" strategy="afterInteractive">
          {`window.N8N_WEBHOOK_URL = 'https://agente.medicamentum360.com/webhook/dr-medici-chat';`}
        </Script>

        {/* Inicialización del widget */}
        <Script src="/widget/embed-snippet.js" strategy="afterInteractive" />
      </body>
    </html>
  );
}
```

---

## ☁️ Despliegue en OCI (Oracle Cloud)

La guía completa de despliegue paso a paso está en: **[📄 docs/GUIA_DESPLIEGUE_OCI.md](./docs/GUIA_DESPLIEGUE_OCI.md)**

Resumen rápido:

```bash
# 1. Crear instancia OCI Compute (Ubuntu 24.04, VM.Standard.E2.2)
# 2. Configurar Security List: puertos 22, 80, 443
# 3. Conectar vía SSH e instalar Docker + Git
ssh ubuntu@<IP_OCI>
curl -fsSL https://get.docker.com | sudo bash
sudo apt install -y docker-compose-v2

# 4. Clonar, configurar y desplegar
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent
cp .env.example .env  # editar API keys
docker compose up -d

# 5. Configurar SSL con Let's Encrypt
# (ver GUIA_DESPLIEGUE_OCI.md §5)

# 6. Probar
curl http://<IP_OCI>/widget
```

---

## 📊 Métricas y monitoreo

| Métrica | Endpoint |
|---|---|
| Health API | `GET /health` en Knowledge API |
| Health n8n | `GET http://n8n:5678/healthz` |
| Health Qdrant | `GET http://qdrant:6333/health` |
| Colecciones Qdrant | `GET http://qdrant:6333/collections` |
| Logs | `docker compose logs -f [n8n|knowledge-api|qdrant]` |

---

## ⚙️ Variables de entorno clave

| Variable | Descripción | Default |
|---|---|---|
| `OPENAI_API_KEY` | API Key de OpenAI (para LLM + embeddings) | — |
| `GOOGLE_API_KEY` | API Key de Google AI Studio (alternativa) | — |
| `N8N_ENCRYPTION_KEY` | Clave de cifrado de n8n (min 32 chars) | — |
| `EMBEDDING_PROVIDER` | `sentence_transformers`, `openai`, `google` | `sentence_transformers` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `paraphrase-multilingual-MiniLM-L12-v2` |
| `SEARCH_TOP_K` | Chunks recuperados por búsqueda | `5` |
| `DOMAIN` | Dominio para SSL en producción | — |

---

## 🧪 Testing manual

```bash
# 1. Probar la API de búsqueda
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"política de reembolso","top_k":3}' | jq .

# 2. Probar el webhook de n8n (simulando el widget)
curl -X POST http://localhost:5678/webhook/dr-medici-chat \
  -H "Content-Type: application/json" \
  -d '{"chatInput":"¿Cómo compro un curso para mi hospital?","sessionId":"test-123"}' \
  --max-time 30

# 3. Reindexar la base de conocimiento
docker compose exec knowledge-api python3 src/ingest.py --recreate
```

---

## 🔄 Roadmap

- [x] RAG con búsqueda semántica vectorial
- [x] Interfaz de chat embebible (@n8n/chat SDK)
- [x] Docker Compose multi-servicio
- [x] Guía de despliegue en OCI + SSL
- [x] Anti-alucinación: solo responde con datos verificados
- [x] Citación de fuentes en cada respuesta
- [x] Personalidad y tono de voz definidos (Dr. Medici)
- [ ] Memoria conversacional multi-turno
- [ ] Integración con Google Calendar (agendar demostraciones)
- [ ] Canal WhatsApp (WhatsApp Business API)
- [ ] Dashboard de analíticas de uso del agente
- [ ] Soporte multi-idioma (EN/PT)
- [ ] Agente multi-modal (responder con imágenes/diagramas)

---

## 👤 Autor

**William** — Challenge Alura Agente (Oracle Next Education + Alura Latam)

Proyecto desarrollado como parte del programa **ONE (Oracle Next Education)** de Alura Latam, especialización en **Orquestación de Agentes IA**.

---

## 📜 Licencia

MIT License — ver [LICENSE](./LICENSE)

---

**¿Preguntas?** El Dr. Medici está aquí para ayudarte. 🩺
