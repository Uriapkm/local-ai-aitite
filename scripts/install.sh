#!/bin/bash
# Instalación - Abuelo IA Assistant
set -e

echo "🚀 Instalando Abuelo IA Assistant"

GREEN='\033[0;32m'
NC='\033[0m'

print_info() { echo -e "${GREEN}✓${NC} $1"; }

print_info "Actualizando sistema..."
sudo dnf upgrade --refresh -y

print_info "Instalando dependencias..."
sudo dnf install -y python3 python3-pip git curl wget \
    portaudio-devel libsndfile-devel ffmpeg \
    vulkan-loader mesa-vulkan-drivers ollama \
    arduino-core

print_info "Configurando Python..."
[ -d "venv" ] && rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

print_info "Instalando paquetes..."
pip install -r requirements.txt

print_info "Descargando modelos..."
ollama pull gemma4:4b-instruct-q4_K_M

print_info "Configurando permisos..."
sudo usermod -aG video $USER
sudo setfacl -m u:$USER:rw /dev/ttyUSB0 2>/dev/null || true

echo ""
print_info "✅ Instalación completada"
echo "Ejecutar: source venv/bin/activate && python src/agent/abuelo_agent.py"
