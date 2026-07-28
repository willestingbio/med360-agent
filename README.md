# 🩺 medicalMen — Agente IA de Medicamentum360

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?logo=groq&logoColor=white)](https://console.groq.com)
[![Gradio](https://img.shields.io/badge/Gradio-6-FF7C00?logo=gradio&logoColor=white)](https://www.gradio.app/)
[![Docker](https://img.shields.io/badge/Docker-Producción-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![OCI](https://img.shields.io/badge/Deploy-OCI_Free_Tier-F80000?logo=oracle&logoColor=white)](https://cloud.oracle.com)
[![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639?logo=nginx&logoColor=white)](https://nginx.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Agente de inteligencia artificial con RAG para Medicamentum360 — plataforma SaaS de e-learning médico en Colombia.**

medicalMen es un chatbot especializado que responde preguntas sobre la plataforma usando **Groq (Llama 3.3 70B, gratuito)** enriquecido con una base de conocimiento de 1,525 líneas de documentación oficial. Desplegado en producción con Docker + Nginx en Oracle Cloud.

---

## 🎓 Challenge Alura Agente — ONE + Alura Latam

Proyecto desarrollado para el **Challenge Alura Agente** del programa **Oracle Next Education (ONE)** de **Alura Latam** — especialización en **Orquestación de Agentes IA**.

---

## 🏗️ Arquitectura completa

```
┌──────────────────────────────────────────────────────────────────┐
│                        🌐 INTERNET                                │
│   Usuario → http://157.xxx.xxx.xxx  (o dominio con HTTPS)        │
└─────────────────────────────┬────────────────────────────────────┘
                              │
              ┌───────────────▼────────────────┐
              │     ☁️ Oracle Cloud (OCI)        │
              │  VM.Standard.E2.1.Micro (Free)  │
              │  ┌──────────────────────────┐   │
              │  │  🔀 Nginx (:80/:443)      │   │
              │  │  Reverse Proxy + Cache    │   │
              │  │  WebSocket para Gradio    │   │
              │  └──────────┬───────────────┘   │
              │             │                    │
              │  ┌──────────▼───────────────┐   │
              │  │  🐳 Docker Container       │   │
              │  │  ┌──────────────────────┐ │   │
              │  │  │  🎨 Gradio UI         │ │   │
              │  │  │  Tema oscuro púrpura  │ │   │
              │  │  └──────────┬───────────┘ │   │
              │  │             │              │   │
              │  │  ┌──────────▼───────────┐ │   │
              │  │  │  🧠 Chat Engine       │ │   │
              │  │  │  1. Respuesta directa │ │   │
              │  │  │  2. Groq (primario)   │ │   │
              │  │  │  3. KB TF-IDF (fallb) │ │   │
              │  │  └──────────┬───────────┘ │   │
              │  │             │              │   │
              │  └─────────────┼──────────────┘   │
              └────────────────┼──────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │         🌐 APIs Externas          │
              │  ┌────────────────────────────┐  │
              │  │  🤖 Groq API (gratis)       │  │
              │  │  Llama 3.3 70B              │  │
              │  │  ~300 tokens/segundo        │  │
              │  └────────────────────────────┘  │
              │  ┌────────────────────────────┐  │
              │  │  📚 Knowledge Base (local)  │  │
              │  │  237 chunks TF-IDF          │  │
              │  │  5 documentos Markdown      │  │
              │  │  1,525 líneas               │  │
              │  └────────────────────────────┘  │
              └─────────────────────────────────┘
```

### Flujo de una consulta

```
1. Usuario escribe pregunta
         │
         ▼
2. ¿Es saludo/identidad? ──SÍ──► Respuesta directa predefinida
         │
        NO
         │
         ▼
3. Búsqueda TF-IDF en KB local (237 chunks)
         │
         ▼
4. Groq API (Llama 3.3 70B)
   Recibe: system prompt + contexto KB + pregunta
         │
    ┌────┴────┐
   OK        FALLO
    │          │
    ▼          ▼
5. Respuesta   5. KB directa
   Groq          o mensaje
                 de ayuda
```

### Integración dual

| Componente | Stack | Ubicación |
|---|---|---|
| **Demo pública** | Python + Gradio + Docker + Nginx | Desplegado en OCI |
| **Widget Medicamentum360** | React + Next.js 15 + Groq | `medicamentumSAAS/components/chat/ChatWidget.tsx` |

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Por qué |
|---|---|---|
| LLM | **Groq + Llama 3.3 70B** | Gratis (sin tarjeta), 300 tok/s, excelente español |
| UI | **Gradio 6** | Profesional, tema personalizable, WebSocket nativo |
| Búsqueda | **TF-IDF (Python)** | Sin dependencias externas, instantáneo, 237 chunks |
| Base conocimiento | **Markdown → JSON** | 5 documentos, 1,525 líneas |
| Contenedor | **Docker + Compose** | Portátil, reproducible, healthchecks |
| Proxy | **Nginx** | Reverse proxy, WebSocket, caché, SSL ready |
| Cloud | **OCI Free Tier** | VM.Standard.E2.1.Micro (1 OCPU, 1 GB) |
| Despliegue | **Git + Docker Compose** | `git pull && docker compose up -d --build` |

---

## 💬 Ejemplos de conversación

```
Usuario: Hola
medicalMen: ¡Hola! 👋 Soy medicalMen 🩺, el asistente virtual de
            Medicamentum360. Pregúntame sobre cursos, precios,
            reembolsos, cómo vender tus cursos o capacitación
            corporativa. ¿En qué te ayudo?

Usuario: ¿Cómo se paga en la plataforma?
medicalMen: Medicamentum360 usa Wompi como pasarela de pagos.
            Acepta tarjetas crédito/débito (Visa, Mastercard),
            PSE, Nequi y Daviplata. El IVA es del 19% y se
            desglosa en el checkout. No hay suscripción mensual —
            pagas por cada curso que compras.
            📄 Fuente: planes-precios

Usuario: Quiero vender mis cursos, ¿cómo empiezo?
medicalMen: ¡Genial! Convertirte en vendor es fácil:
            1. Regístrate como usuario normal
            2. Ve a /vender y completa tu perfil
            3. Sube tus datos fiscales y bancarios
            4. El equipo revisa (máx 48 horas)
            5. Una vez aprobado, entra a /instructor
            Recibes el 80% de cada venta.
            📄 Fuente: conocimiento-producto
```

---

## 🚀 Instalación local

```bash
# 1. Clonar
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent

# 2. Entorno virtual
python3 -m venv .venv && source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. API key de Groq (gratis: console.groq.com/keys)
export GROQ_API_KEY=gsk_tu_key

# 5. Ejecutar
python app.py
# Abre http://localhost:7860
```

---

## 🐳 Docker (producción)

```bash
# Local
echo "GROQ_API_KEY=gsk_tu_key" > .env
docker compose up -d
# http://localhost

# Producción (OCI)
# Ver guía completa: docs/GUIA_DESPLIEGUE_OCI.md
```

---

## ☁️ Despliegue en OCI (producción)

Guía completa: **[docs/GUIA_DESPLIEGUE_OCI.md](docs/GUIA_DESPLIEGUE_OCI.md)**

Resumen rápido:

```bash
# En la instancia OCI (Ubuntu 24.04)
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent
echo "GROQ_API_KEY=gsk_tu_key" > .env
docker compose up -d
# http://<IP_OCI>
```

---

## 📁 Estructura del repositorio

```
med360-agent/
│
├── app.py                          ← Aplicación principal (Gradio + Groq + RAG)
├── Dockerfile                      ← Imagen Docker para producción
├── docker-compose.yml              ← Orquestación (app + Nginx)
├── requirements.txt                ← Dependencias Python
├── .env.example                   ← Template de variables
├── .dockerignore                  ← Exclusiones de build
├── .gitignore                     ← Exclusiones de git
├── README.md                      ← Este archivo
├── LICENSE                        ← MIT
│
├── data/
│   ├── .gitkeep
│   └── kb_chunks.json             ← KB preprocesada (237 chunks TF-IDF)
│
├── knowledge-base/                 ← Fuentes Markdown originales
│   ├── conocimiento-producto.md
│   ├── faq-soporte.md
│   ├── planes-precios.md
│   ├── politica-privacidad.md
│   └── terminos-uso.md
│
├── nginx/
│   ├── nginx.conf                 ← Config principal Nginx
│   └── conf.d/
│       └── medicalmen.conf        ← Virtual host producción
│
├── docs/
│   └── GUIA_DESPLIEGUE_OCI.md     ← Guía completa paso a paso
│
├── widget/                         ← Widget standalone HTML (legacy)
│   └── dr-medici-standalone.html
│
└── evidencias/                    ← Capturas del Challenge
```

---

## 🔐 Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `GROQ_API_KEY` | **Obligatoria.** Key gratuita de Groq | — |
| `GROQ_MODEL` | Modelo LLM | `llama-3.3-70b-versatile` |
| `PORT` | Puerto del servidor Gradio | `7860` |

---

## 🔒 Seguridad

- API key en `.env` (nunca en código, en `.gitignore`)
- Nginx como reverse proxy (no exponer Gradio directamente)
- Sistema anti-alucinación: solo responde con datos verificados
- Todas las respuestas citan la fuente del documento original
- Rate limiting vía Nginx (configurable)
- HTTPS con Let's Encrypt (guía incluida en docs/)

---

## 👤 Autor

**William Esteban** — Challenge Alura Agente

- GitHub: [willestingbio](https://github.com/willestingbio)
- Repositorio principal: [medicamentumSAAS](https://github.com/willestingbio/medicamentumSAAS)
- Programa: Oracle Next Education (ONE) + Alura Latam

---

## 📜 Licencia

MIT License — ver [LICENSE](LICENSE)

---

**¿Preguntas?** medicalMen está aquí para ayudarte. 🩺
