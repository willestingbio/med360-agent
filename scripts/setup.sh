#!/bin/bash
# ── setup.sh — One-command setup ──────────────────────
# Clona la base de conocimiento desde Medicamentum360 y levanta los servicios
set -e

echo "=== Med360 Agent — Setup ==="

# Verificar requisitos
command -v docker >/dev/null 2>&1 || { echo "❌ Docker no encontrado. Instálalo primero."; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose no encontrado."; exit 1; }

# Copiar base de conocimiento si no existe
if [ ! -f "knowledge-base/conocimiento-producto.md" ]; then
    echo "📚 Copiando base de conocimiento..."
    mkdir -p knowledge-base
    if [ -d "../medicamentumSAAS/.agents/knowledge-base" ]; then
        cp ../medicamentumSAAS/.agents/knowledge-base/*.md knowledge-base/ 2>/dev/null || true
        echo "  ✓ Documentos copiados desde medicamentumSAAS"
    else
        echo "  ⚠ No se encontró la base de conocimiento. Cópiala manualmente a knowledge-base/"
    fi
fi

# Crear .env si no existe
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✓ .env creado desde .env.example"
    echo "  ⚠ Edita .env con tus claves API antes de continuar"
fi

# Iniciar servicios
echo ""
echo "🐳 Iniciando Docker Compose..."
docker compose up -d

echo ""
echo "=== Setup completado ==="
echo "📊 n8n Editor:       http://localhost:5678"
echo "🔍 Knowledge API:    http://localhost:8001/docs"
echo "💬 Widget Demo:      http://localhost/widget"
echo ""
echo "📌 Próximos pasos:"
echo "  1. Abre http://localhost:5678 e importa el workflow desde n8n-workflows/dr-medici-agent.json"
echo "  2. Configura el nodo AI Agent con tu LLM (OpenAI, Google, Cohere)"
echo "  3. Activa el workflow"
echo "  4. Prueba el chat en http://localhost/widget"
