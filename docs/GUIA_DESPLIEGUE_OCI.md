# Guía de Despliegue en Oracle Cloud Infrastructure (OCI)

**medicalMen — Agente IA de Medicamentum360**

---

## 📋 Requisitos previos

| Requisito | Dónde conseguirlo |
|---|---|
| Cuenta Oracle Cloud (Free Tier) | [signup.oracle.com](https://signup.oracle.com) |
| API Key de Groq (gratis) | [console.groq.com/keys](https://console.groq.com/keys) |
| Git | `sudo apt install -y git` |
| Dominio (opcional, para HTTPS) | Namecheap, GoDaddy, etc. |

---

## 🚀 Despliegue — paso a paso

### 1. Crear instancia OCI

1. Abre [cloud.oracle.com](https://cloud.oracle.com) → **Compute → Instances → Create instance**

2. Configura:

| Campo | Valor |
|---|---|
| Name | `medicalmen` |
| Image | **Canonical Ubuntu 24.04 LTS** |
| Shape | **VM.Standard.E2.1.Micro** (Free Tier) |
| SSH key | Sube tu clave pública |

3. En **Security List**, agrega reglas de ingreso:

| Source | Puerto | Descripción |
|---|---|---|
| `0.0.0.0/0` | 22 | SSH |
| `0.0.0.0/0` | 80 | HTTP |
| `0.0.0.0/0` | 443 | HTTPS (si tienes dominio) |

4. Clic **Create**. Cuando diga "Running", asigna IP pública:
   - Ve a la instancia → **Attached VNICs** → clic en el VNIC
   - **IPv4 Addresses** → **Assign public IP** → Ephemeral
   - Anota la IP (ej: `157.xxx.xxx.xxx`)

---

### 2. Conectar e instalar

```bash
# Conectar (usa tu IP y tu llave SSH)
ssh -i tu_llave.key ubuntu@<IP_PUBLICA>

# Instalar Docker + Git
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker ubuntu
newgrp docker
sudo apt install -y git
```

---

### 3. Clonar y desplegar

```bash
# Clonar
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent

# Configurar API key de Groq
# Obtén la tuya gratis en: https://console.groq.com/keys
echo "GROQ_API_KEY=gsk_tu_key_aqui" > .env

# Desplegar con Docker Compose
docker compose up -d
```

---

### 4. Probar

Abre tu navegador y visita:

```
http://<IP_PUBLICA>
```

Debes ver la interfaz de medicalMen con el chat. Escribe "hola" o cualquier pregunta de ejemplo.

**¿No funciona?** Verifica:

```bash
# Ver logs
docker compose logs -f app

# Verificar contenedor
docker compose ps

# Probar localmente
curl http://localhost:7860
```

---

### 5. (Opcional) Dominio + HTTPS con Let's Encrypt

Si tienes un dominio (ej: `agente.medicamentum360.com`):

```bash
# Apuntar dominio a la IP de OCI (en tu proveedor de dominio)

# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Parar Docker Nginx (vamos a usar el del sistema)
docker compose stop nginx

# Configurar sitio
sudo tee /etc/nginx/sites-available/medicalmen << 'EOF'
server {
    listen 80;
    server_name agente.medicamentum360.com;

    location /queue/join {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/medicalmen /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Obtener certificado SSL
sudo certbot --nginx -d agente.medicamentum360.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

### 6. Mantenimiento

```bash
# Ver logs en tiempo real
docker compose logs -f app

# Reiniciar después de actualizar código
cd ~/med360-agent
git pull
docker compose up -d --build

# Ver uso de recursos
docker stats medicalmen
```

---

## 🔧 Solución de problemas

| Problema | Solución |
|---|---|
| Connection refused | Verifica que el puerto 7860/80 esté en la Security List |
| 502 Bad Gateway (Nginx) | `docker compose restart app` |
| Sin respuestas de IA | Verifica `GROQ_API_KEY` en `.env`: `cat .env` |
| 403 Forbidden de Groq | La key expiró o no es válida. Crea una nueva en console.groq.com |
| KB vacía (0 chunks) | `ls data/kb_chunks.json` — si no existe, regenera |
| Puerto 7860 no accesible | Asegúrate de haber agregado la regla en Security List |
| SSH timeout | Verifica puerto 22 en Security List y que la IP pública esté asignada |

---

## 📊 Arquitectura de producción

```
Internet → Nginx (:80) → Gradio App (:7860, Docker) → Groq API
                                                          ↓
                                                     KB local (TF-IDF)
```

- **Nginx**: reverse proxy, caching, WebSocket para Gradio
- **Gradio**: interfaz web Python, tema oscuro Medicamentum360
- **Groq**: API gratuita de LLM (Llama 3.3 70B)
- **KB local**: 237 chunks TF-IDF (fallback sin API)
- **Docker Compose**: orquestación de contenedores
- **OCI**: Oracle Cloud Free Tier (VM.Standard.E2.1.Micro)
