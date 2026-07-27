# ── Guía de Despliegue en Oracle Cloud Infrastructure (OCI) ──

**Versión:** 1.0 · **Proyecto:** med360-agent

---

## 1. Requisitos previos

- Cuenta de Oracle Cloud (Free Tier o Pay-As-You-Go)
- Dominio registrado (ej. `agente.medicamentum360.com`)
- Claves API de un proveedor LLM (OpenAI o Google Gemini)
- Git instalado localmente

---

## 2. Crear instancia OCI Compute

### 2.1 Acceder a OCI Console

1. Ve a https://cloud.oracle.com y haz login.
2. Navega a **Compute → Instances**.
3. Haz clic en **Create instance**.

### 2.2 Configuración de la instancia

| Campo | Valor |
|---|---|
| **Name** | `med360-agent` |
| **Placement** | Default |
| **Image** | Ubuntu 24.04 LTS (Canonical) |
| **Shape** | VM.Standard.E2.1.Micro (Free Tier: 1 OCPU, 1 GB RAM) o VM.Standard.E2.2 (2 OCPU, 4 GB RAM recomendado) |
| **Boot volume** | 100 GB (máximo free tier) |
| **SSH key** | Sube tu clave pública SSH o genera una nueva |

### 2.3 Configuración de red

1. En **Networking**, crea una nueva **Virtual Cloud Network (VCN)** si no tienes una.
2. Asegúrate de que la **subnet** tenga acceso a internet (Internet Gateway).
3. Anota la **IP pública** asignada a la instancia.

### 2.4 Security List (Firewall)

Agrega reglas de ingreso:

| Source | Protocol | Port | Description |
|---|---|---|---|
| `0.0.0.0/0` | TCP | 22 | SSH |
| `0.0.0.0/0` | TCP | 80 | HTTP (Let's Encrypt + Nginx) |
| `0.0.0.0/0` | TCP | 443 | HTTPS (Nginx) |

---

## 3. Conectar y configurar la instancia

```bash
# Conectar vía SSH
ssh ubuntu@<IP_PUBLICA_OCI>

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install -y docker-compose-v2

# Cerrar sesión y reconectar para aplicar grupo docker
exit
ssh ubuntu@<IP_PUBLICA_OCI>
```

---

## 4. Clonar y desplegar el proyecto

```bash
# Clonar repositorio
git clone https://github.com/<TU_USUARIO>/med360-agent.git
cd med360-agent

# Copiar y configurar variables
cp .env.example .env
nano .env   # ← Configurar OPENAI_API_KEY y N8N_ENCRYPTION_KEY

# Dar permisos al entrypoint
chmod +x scripts/entrypoint.sh

# Iniciar servicios
docker compose up -d

# Verificar que todo está corriendo
docker compose ps
# Deberías ver: n8n, qdrant, knowledge-api, nginx en estado "Up"
```

---

## 5. Configurar SSL con Let's Encrypt

### Opción A: Certbot standalone

```bash
# Detener Nginx temporalmente
docker compose stop nginx

# Generar certificado
sudo docker run -it --rm \
  -v $(pwd)/certbot_data:/etc/letsencrypt \
  -v $(pwd)/certbot_www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d agente.medicamentum360.com \
  --email tu-email@medicamentum360.com \
  --agree-tos --non-interactive

# Iniciar Nginx nuevamente
docker compose up -d nginx
```

### Opción B: Usando el contenedor de certbot

1. Edita `nginx/conf.d/med360-agent.conf` y descomenta la redirección HTTPS.
2. Agrega el bloque SSL:

```nginx
server {
    listen 443 ssl;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... mismos location blocks que el bloque HTTP
}
```

3. Reinicia: `docker compose restart nginx`

---

## 6. Configurar n8n

1. Accede a `http://<IP_PUBLICA>:5678` (o `https://agente.medicamentum360.com` si ya tienes SSL).
2. Crea una cuenta de administrador para n8n (solo visible en primer acceso).
3. Ve a **Settings → Community Nodes** y habilita `@n8n/n8n-nodes-langchain`.
4. Ve a **Workflows → Import from File** y selecciona `n8n-workflows/dr-medici-agent.json`.
5. Configura el nodo **AI Agent**:
   - Selecciona tu proveedor de LLM (OpenAI / Google Gemini).
   - Ingresa la API Key correspondiente.
   - Configura el modelo (ej. `gpt-4o` o `gemini-flash-latest`).
6. Configura el nodo **buscar_base_conocimiento** (HTTP Request):
   - La URL debe ser `http://knowledge-api:8001/search` (Docker network interna).
7. Haz clic en **Activate** (interruptor arriba a la derecha).
8. Copia la URL del webhook (aparece en el nodo "Chat Webhook").

---

## 7. Probar el widget

1. Abre `http://<IP_PUBLICA>/widget` (o tu dominio con HTTPS).
2. Escribe una pregunta de prueba: *"¿Cómo funciona el marketplace de Medicamentum360?"*
3. El agente debe responder con información verificada de la base de conocimiento.

---

## 8. Integrar con Medicamentum360 (Next.js)

Agrega al layout de tu app Next.js:

```tsx
// app/layout.tsx
import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        {children}
        <Script
          src="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js"
          strategy="afterInteractive"
        />
        <Script id="dr-medici-config" strategy="afterInteractive">
          {`window.N8N_WEBHOOK_URL = 'https://agente.medicamentum360.com/webhook/dr-medici-chat';`}
        </Script>
        <Script
          src="/widget/embed-snippet.js"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
```

---

## 9. Monitoreo y mantenimiento

```bash
# Ver logs
docker compose logs -f n8n
docker compose logs -f knowledge-api

# Reiniciar servicios
docker compose restart

# Actualizar imágenes
docker compose pull
docker compose up -d

# Backup de Qdrant
docker compose stop qdrant
tar -czf qdrant_backup_$(date +%Y%m%d).tar.gz qdrant_data/
docker compose start qdrant

# Reindexar base de conocimiento (si se actualizan los docs)
docker compose exec knowledge-api python3 src/ingest.py --recreate
```

---

## 10. Troubleshooting

| Problema | Solución |
|---|---|
| n8n no arranca | Verificar `N8N_ENCRYPTION_KEY` en `.env` (debe tener al menos 32 caracteres) |
| Knowledge API no encuentra Qdrant | Verificar que `QDRANT_HOST=qdrant` y que el servicio qdrant está Up |
| El chat responde "No encontré información" | Ejecutar ingestión: `docker compose exec knowledge-api python3 src/ingest.py --recreate` |
| Error de CORS en el widget | Verificar que la URL del webhook de n8n es correcta y accesible |
| El modelo de embeddings tarda en cargar | La primera vez descarga ~120 MB del modelo. Esperar unos minutos. |
| OCI Free Tier: recursos insuficientes | El modelo de embeddings necesita ~512 MB RAM. Considera usar embeddings vía API (OpenAI/Google) en vez de local. |
