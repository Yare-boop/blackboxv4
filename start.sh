#!/bin/bash
# start.sh — Arrancar Blackbox completo
# Uso: bash start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "  ⬛  BLACKBOX arrancando..."
echo ""

# Matar procesos previos en esos puertos
pkill -f "server.py" 2>/dev/null
pkill -f "http.server 8080" 2>/dev/null
sleep 1

# Arrancar backend Flask en background
echo "  🐉 Backend Flask en puerto 5000..."
python server.py &
BACKEND_PID=$!
sleep 2

# Verificar que arrancó
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "  ⚠  Error al arrancar el backend"
    exit 1
fi

# Arrancar frontend HTTP server en background
echo "  ♫  Frontend en puerto 8080..."
python -m http.server 8080 &
FRONTEND_PID=$!
sleep 1

echo ""
echo "  ✦  Blackbox corriendo"
echo ""
echo "  Abre en el navegador:"
echo "  → http://localhost:8080"
echo ""
echo "  Ctrl+C para detener todo"
echo ""

# Guardar PIDs
echo $BACKEND_PID > /tmp/blackbox_backend.pid
echo $FRONTEND_PID > /tmp/blackbox_frontend.pid

# Esperar — Ctrl+C mata ambos
trap "echo ''; echo '  ⬛ Cerrando Blackbox...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
