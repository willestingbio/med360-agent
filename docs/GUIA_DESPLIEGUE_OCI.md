# Guía de Despliegue en Oracle Cloud Infrastructure (OCI)

**medicalMen — Agente IA de Medicamentum360**

---

## 1. Requisitos previos

- Cuenta Oracle Cloud (Free Tier: [signup.oracle.com](https://signup.oracle.com))
- Clave API de Groq (gratis: [console.groq.com/keys](https://console.groq.com/keys))
- Git instalado

---

## 2. Crear instancia OCI Compute

1. Ve a https://cloud.oracle.com → **Compute → Instances**
2. Clic en **Create instance**
3. Configura:

| Campo | Valor |
|---|---|
| Name | `medicalmen` |
| Image | Ubuntu 24.04 LTS |
| Shape | VM.Standard.E2.1.Micro (Free Tier: 1 OCPU, 1 GB RAM) |
| Boot volume | 50 GB |
| SSH key | Sube tu clave pública |

4. En **Networking**, crea una VCN si no tienes. Asegúrate de que la subnet tenga Internet Gateway.
5. En **Security List**, agrega reglas de ingreso:

| Source | Puerto | Descripción |
|---|---|---|
| 0.0.0.0/0 | 22 | SSH |
| 0.0.0.0/0 | 7860 | Gradio (prueba) |
| 0.0.0.0/0 | 80 | HTTP (opcional con Nginx) |
| 0.0.0.0/0 | 443 | HTTPS (opcional con SSL) |

6. Clic en **Create** y espera a que esté **Running**.
7. Anota la **Public IP**.

---

## 3. Conectar e instalar

```bash
# Conectar por SSH
ssh ubuntu@<IP_PUBLICA>

# Instalar Docker
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker ubuntu
newgrp docker

# Instalar Git
sudo apt install -y git
```

---

## 4. Clonar y desplegar

```bash
# Clonar repositorio
git clone https://github.com/willestingbio/med360-agent.git
cd med360-agent

# Configurar API key de Groq
echo "GROQ_API_KEY=gsk_tu_key_aqui" > .env

# Levantar con Docker Compose
docker compose up -d

# Verificar que está corriendo
docker compose ps
# Debe mostrar: medicalmen → Up
```

---

## 5. Probar

```bash
# Probar localmente en el servidor
curl http://localhost:7860

# Desde tu navegador
# Abre: http://<IP_PUBLICA>:7860
```

---

## 6. (Opcional) Nginx + SSL + Dominio

```bash
# Instalar Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Crear config
sudo tee /etc/nginx/sites-available/medicalmen << 'EOF'
server {
    listen 80;
    server_name agente.medicamentum360.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
EOF

# Activar sitio
sudo ln -s /etc/nginx/sites-available/medicalmen /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# SSL con Let's Encrypt
sudo certbot --nginx -d agente.medicamentum360.com
```

---

## 7. Actualizar la aplicación

```bash
cd ~/med360-agent
git pull
docker compose up -d --build
```

---

## 8. Solución de problemas

```bash
# Ver logs
docker compose logs -f app

# Reiniciar
docker compose restart app

# Reconstruir desde cero
docker compose down
docker compose up -d --build
```
