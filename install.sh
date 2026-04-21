#!/bin/bash
# install.sh — Setup de Blackbox en Termux
# Uso: bash install.sh

echo ""
echo "  ⬛  BLACKBOX — Setup en Termux"
echo ""

# Actualizar paquetes
echo "▸ Actualizando paquetes..."
pkg update -y && pkg upgrade -y

# Instalar dependencias del sistema
echo "▸ Instalando python, ffmpeg, git..."
pkg install -y python ffmpeg git

# Instalar dependencias de Python
echo "▸ Instalando flask, yt-dlp..."
pip install flask flask-cors yt-dlp

# Dar permisos de almacenamiento (para acceder a descargas del cel)
echo "▸ Solicitando permisos de almacenamiento..."
termux-setup-storage

echo ""
echo "  ✦  Instalación completa"
echo ""
echo "  Para arrancar Blackbox:"
echo "    bash start.sh"
echo ""
