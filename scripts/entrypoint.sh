#!/bin/bash
# ── entrypoint.sh — Knowledge API startup ──────────────
set -e

echo "=== Med360 Knowledge API Entrypoint ==="

python3 -c "
import urllib.request, time, os
host = os.environ.get('QDRANT_HOST','qdrant')
port = os.environ.get('QDRANT_PORT','6333')
for i in range(30):
    try:
        urllib.request.urlopen(f'http://{host}:{port}', timeout=2)
        print('✓ Qdrant disponible')
        break
    except Exception:
        print(f'  Esperando Qdrant... ({i+1}/30)')
        time.sleep(2)
else:
    print('⚠ Qdrant no disponible, continuando...')
"

python3 -c "
import urllib.request, json, os, subprocess, sys
host = os.environ.get('QDRANT_HOST','qdrant')
port = os.environ.get('QDRANT_PORT','6333')
collection = os.environ.get('QDRANT_COLLECTION','med360_knowledge')
needs_ingestion = True
try:
    req = urllib.request.Request(f'http://{host}:{port}/collections/{collection}')
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read())
    points = data.get('result',{}).get('points_count',0)
    print(f'Colección {collection}: {points} vectores')
    if points and points > 0:
        needs_ingestion = False
        print('✓ Base poblada, sin ingestión necesaria')
except Exception as e:
    err = str(e)
    if '404' in err or 'Not Found' in err:
        print('Colección no existe, se creará en ingestión')
    else:
        print(f'⚠ {err}')

if needs_ingestion:
    print('Ejecutando ingestión inicial (descargando modelo ~120MB)...')
    result = subprocess.run([sys.executable, 'src/ingest.py'], cwd='/app')
    if result.returncode != 0:
        print('⚠ Ingestión falló, la API iniciará igual (reintenta con docker compose exec knowledge-api python3 src/ingest.py --recreate)')
"

echo "Iniciando Knowledge API en 0.0.0.0:8001..."
exec python3 src/api.py
