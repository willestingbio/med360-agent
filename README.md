# 🩺 medicalMen — Agente IA de Medicamentum360

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036)](https://console.groq.com)
[![Gradio](https://img.shields.io/badge/Gradio-UI-FF7C00)](https://www.gradio.app/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![OCI](https://img.shields.io/badge/Deploy-OCI-F80000?logo=oracle)](https://cloud.oracle.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Asistente virtual con IA para Medicamentum360 — plataforma SaaS de e-learning médico.**

medicalMen responde preguntas sobre cursos, marketplace, precios, reembolsos y capacitación corporativa usando **Groq (Llama 3.3 70B, gratuito)** + RAG con base de conocimiento de 1,525 líneas.

---

## 🎓 Challenge Alura Agente — ONE + Alura Latam

Proyecto desarrollado para el desafío **Alura Agente** del programa **Oracle Next Education (ONE)** + **Alura Latam** — especialización en Orquestación de Agentes IA.

---

## 🏗️ Arquitectura

```
┌──────────────────────┐     ┌──────────────────────┐
│  Medicamentum360      │     │  Demo pública (OCI)   │
│  ┌──────────────────┐ │     │  ┌──────────────────┐ │
│  │ ChatWidget React  │ │     │  │ Gradio UI        │ │
│  │ (Next.js)         │ │     │  │ app.py           │ │
│  └────────┬─────────┘ │     │  └────────┬─────────┘ │
└───────────┼───────────┘     └───────────┼───────────┘
            │                              │
            └──────────┬───────────────────┘
                       ▼
            ┌──────────────────┐
            │  Groq API (gratis) │
            │  Llama 3.3 70B    │
            └────────┬─────────┘
                     ▼
            ┌──────────────────┐
            │  Base Conocimiento│
            │  237 chunks (MD)  │
            │  TF-IDF search    │
            └──────────────────┘
```

### Integraciones

| Componente | Stack | Ubicación |
|---|---|---|
| **Widget en Medicamentum360** | React + Next.js 15 | `medicamentumSAAS/components/chat/ChatWidget.tsx` |
| **Demo pública standalone** | Python + Gradio | `med360-agent/app.py` |
| **Base de conocimiento** | Markdown → JSON chunks | `data/kb_chunks.json` (237 chunks) |

---

## 💬 Ejemplos

> **Usuario:** "¿Qué es Medicamentum360?"
>
> **medicalMen:** "Medicamentum360 es una plataforma SaaS de e-learning y marketplace para el sector salud en Colombia. Permite a hospitales, clínicas y profesionales comprar, crear y vender cursos médicos, experiencias VR y automatizaciones clínicas."

> **Usuario:** "¿Cómo vender mis cursos?"
>
> **medicalMen:** "Regístrate → ve a /vender → completa tu perfil y datos fiscales → el equipo revisa (máx 48h) → accede a /instructor para crear tu primer curso. Recibes el 80% de cada venta."

> **Usuario:** "¿Política de reembolso?"
>
> **medicalMen:** "7 días desde la compra, con menos del 20% de progreso. Ve a /orders y haz clic en 'Solicitar reembolso'. El equipo revisa cada caso."

---

## 🚀 Instalación local

```bash
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent

# Entorno virtual
python -m venv .venv && source .venv/bin/activate

# Dependencias
pip install -r requirements.txt

# API key (gratis: https://console.groq.com/keys)
export GROQ_API_KEY=gsk_tu_key

# Ejecutar
python app.py
# http://localhost:7860
```

## 🐳 Docker

```bash
docker build -t medicalmen .
docker run -p 7860:7860 -e GROQ_API_KEY=gsk_tu_key medicalmen
```

## ☁️ Despliegue en OCI

Ver guía completa: [docs/GUIA_DESPLIEGUE_OCI.md](docs/GUIA_DESPLIEGUE_OCI.md)

```bash
# En la instancia OCI
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent
echo "GROQ_API_KEY=gsk_tu_key" > .env
docker compose up -d
# http://<IP_OCI>:7860
```

---

## 📁 Estructura

```
med360-agent/
├── app.py                     ← Demo pública (Gradio + Groq + RAG)
├── Dockerfile                 ← Contenedor para OCI/Cloud Run
├── docker-compose.yml         ← Orquestación producción
├── requirements.txt           ← Dependencias Python
├── .env.example              ← Template variables
├── README.md                 ← Este archivo
│
├── data/
│   └── kb_chunks.json        ← KB preprocesada (237 chunks)
│
├── knowledge-base/            ← Fuentes Markdown
│   ├── conocimiento-producto.md
│   ├── faq-soporte.md
│   ├── planes-precios.md
│   ├── politica-privacidad.md
│   └── terminos-uso.md
│
├── widget/                    ← Widget standalone HTML
├── docs/                      ← Guías de despliegue
│   └── GUIA_DESPLIEGUE_OCI.md
│
└── evidencias/               ← Capturas del challenge
```

---

## 🔐 Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `GROQ_API_KEY` | Key de Groq (gratis: console.groq.com/keys) | — |
| `GROQ_MODEL` | Modelo LLM | `llama-3.3-70b-versatile` |
| `PORT` | Puerto del servidor | `7860` |

---

## 👤 Autor

**William Esteban** — Challenge Alura Agente (ONE + Alura Latam)

- GitHub: [willestingbio](https://github.com/willestingbio)
- Repositorio principal: [medicamentumSAAS](https://github.com/willestingbio/medicamentumSAAS)

## 📜 Licencia

MIT
