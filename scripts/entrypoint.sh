#!/bin/bash
# ── entrypoint.sh — Knowledge API startup ──────────────
# 1. Espera a que Qdrant esté disponible
# 2. Ejecuta ingestión si no hay datos
# 3. Inicia la API

set -e

echo "=== Med360 Knowledge API Entrypoint ==="
echo "Esperando a Qdrant en ${QDRANT_HOST}:${QDRANT_PORT}..."

# Esperar a Qdrant
for i in $(seq 1 30); do
    if curl -sf "http://${QDRANT_HOST}:${QDRANT_PORT}/health" > /dev/null 2>&1; then
        echo "✓ Qdrant disponible"
        break
    fi
    echo "  Esperando Qdrant... (intento $i/30)"
    sleep 2
done

# Verificar si ya hay datos en Qdrant
POINTS=$(curl -sf "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_COLLECTION}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('points_count',0))" 2>/dev/null || echo "0")

if [ "$POINTS" = "0" ] || [ "$POINTS" = "" ]; then
    echo "Base de conocimiento vacía. Ejecutando ingestión inicial..."
    cd /app && python3 src/ingest.py
    echo "✓ Ingestión completada"
else
    echo "✓ Base de conocimiento ya poblada (${POINTS} vectores)"
fi

# Iniciar API
echo "Iniciando Knowledge API en ${API_HOST}:${API_PORT}..."
exec python3 src/api.py
