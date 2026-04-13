#!/bin/bash
# Instalación - Abuelo IA con Gemma 4 para AMD BC250
set -e

echo "🚀 Instalando Abuelo IA con Gemma 4 (AMD BC250)"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

print_info "Paso 1/6: Actualizando sistema..."
sudo dnf upgrade --refresh -y
print_success "Sistema actualizado"

print_info "Paso 2/6: Instalando dependencias..."
sudo dnf install -y python3 python3-pip git curl wget \
    portaudio-devel libsndfile-devel ffmpeg \
    vulkan-loader vulkan-tools mesa-vulkan-drivers ollama
print_success "Dependencias instaladas"

print_info "Paso 3/6: Configurando Python..."
[ -d "venv" ] && rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
print_success "Python configurado"

print_info "Paso 4/6: Instalando paquetes Python..."
pip install -r requirements.txt || { print_error "Falló instalación"; exit 1; }
print_success "Paquetes Python instalados"

print_info "Paso 5/6: Descargando Gemma 4..."
ollama pull gemma4:4b-instruct-q4_K_M
print_success "Gemma 4 descargado"

print_info "Paso 6/6: Configurando permisos..."
sudo usermod -aG video $USER
sudo setfacl -m u:$USER:rw /dev/ttyUSB0 2>/dev/null || true
print_success "Permisos configurados"

echo ""
print_success "✅ Instalación completada"
echo "Ejecutar: source venv/bin/activate && python src/agent/abuelo_agent.py"
