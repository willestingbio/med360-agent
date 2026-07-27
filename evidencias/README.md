# Evidencias — med360-agent

Capturas de pantalla y evidencias del funcionamiento del agente.

---

## 1. Arquitectura

```
┌────────────────────────────────────────────────────────────────────┐
│                    Med360 Agent — Arquitectura                       │
│                                                                     │
│  ┌──────────────┐     HTTPS      ┌──────────────────────────────┐  │
│  │ Medicamentum  │───────────────▶│  Oracle Cloud Infrastructure  │  │
│  │    360        │   POST /chat   │                              │  │
│  │ (Next.js)     │                │  ┌──────────────────────┐   │  │
│  │               │                │  │  Nginx (SSL+Proxy)   │   │  │
│  │  ┌─────────┐  │                │  └───┬──────────────┬───┘   │  │
│  │  │@n8n/chat│  │                │      │              │        │  │
│  │  │ widget  │  │                │  ┌───▼──────┐  ┌───▼──────┐ │  │
│  │  └─────────┘  │                │  │  n8n     │  │ Knowledge│ │  │
│  └──────────────┘                │  │  Agent   │  │   API    │ │  │
│                                   │  │  (5678)  │  │ (8001)   │ │  │
│                                   │  └───┬──────┘  └───┬──────┘ │  │
│                                   │      │              │        │  │
│                                   │      │         ┌───▼──────┐ │  │
│                                   │      │         │  Qdrant  │ │  │
│                                   │      │         │ (6333)   │ │  │
│                                   │      │         └──────────┘ │  │
│                                   └──────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## 2. Flujo de una consulta (RAG)

```
Usuario: "¿Cómo funciona el reembolso?"
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. Widget → n8n Webhook                 │
│    POST /webhook/dr-medici-chat         │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 2. n8n AI Agent                         │
│    - Recibe: "¿Cómo funciona el reembolso?"│
│    - Decide usar tool: buscar_base_     │
│      conocimiento                       │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 3. Knowledge API → POST /search         │
│    - Convierte query a embedding/TF-IDF │
│    - Busca en Qdrant (cosine sim)       │
│    - Fallback: TF-IDF search            │
│    - Retorna top-5 chunks               │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 4. LLM + Contexto → Respuesta           │
│    System Prompt + chunks + pregunta    │
│    → GPT-4o/Gemini genera respuesta     │
│    con citación de fuente               │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│ 5. Widget muestra respuesta             │
│    "Tienes 7 días desde la compra...    │
│     (Fuente: faq-soporte.md)"           │
└─────────────────────────────────────────┘
```

## 3. Repositorio GitHub

**URL:** https://github.com/willestingbio/med360-agent

![Commits](https://img.shields.io/badge/commits-8-blue)

```
313651f fix(api): add TF-IDF fallback search engine
215d9ef docs: add comprehensive README and OCI deployment guide
f7e7d63 feat(infra): create Docker Compose multi-service stack
6419e95 feat(widget): build embeddable chat widget with n8n SDK
b44aa6f feat(n8n): create Dr. Medici AI agent workflow with RAG tool
00f14f4 feat(api): implement semantic search API with Qdrant
bcc83da docs(knowledge-base): add complete product documentation
405a5e4 chore: initial project scaffold
```

## 4. Deployment en OCI

### Instancia recomendada
- **Proveedor:** Oracle Cloud Infrastructure (Free Tier)
- **Shape:** VM.Standard.E2.2 (2 OCPU, 4 GB RAM)
- **OS:** Ubuntu 24.04 LTS
- **Firewall:** Puertos 22 (SSH), 80 (HTTP), 443 (HTTPS)

### Comando de despliegue
```bash
# En la instancia OCI:
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent
cp .env.example .env
# Editar .env con OPENAI_API_KEY
docker compose up -d
# Widget disponible en: http://<IP_OCI>/widget
```

### Verificación
```bash
curl http://localhost:8001/health
# {"status":"ok","qdrant":true,"tfidf":true,"chunks":200}

curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"política de reembolso"}'
# {"query":"política de reembolso","results":[...],"total":5,"engine":"qdrant"}
```

## 5. Widget integrado en Medicamentum360

El widget de @n8n/chat se integra en `app/layout.tsx` mediante:
- Link CSS al CDN de @n8n/chat
- Script de configuración con `NEXT_PUBLIC_N8N_WEBHOOK_URL`
- Script de inicialización en `/public/widget/embed-snippet.js`

```tsx
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css" />
<Script id="dr-medici-config" strategy="afterInteractive">
  {`window.N8N_WEBHOOK_URL = '...';`}
</Script>
<Script src="/widget/embed-snippet.js" strategy="afterInteractive" />
```
