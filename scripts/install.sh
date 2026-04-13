#!/bin/bash
# ============================================
# Script de Instalación - Abuelo IA Assistant
# Para Bazzite OS (Fedora Atomic)
# ============================================

set -e  # Salir si hay error

echo "🚀 Iniciando instalación de Abuelo IA Assistant..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar que estamos en Bazzite/Fedora
if [ -f /etc/fedora-release ]; then
    print_info "Detectado Fedora/Bazzite OS"
else
    print_warn "No se detectó Fedora/Bazzite. El script puede no funcionar correctamente."
fi

# ============================================
# 1. Instalar dependencias del sistema
# ============================================
print_info "Instalando dependencias del sistema..."

# Actualizar repositorios
sudo dnf upgrade --refresh -y

# Instalar paquetes básicos
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    gcc-c++ \
    make \
    git \
    ffmpeg \
    portaudio-devel \
    libsndfile \
    alsa-lib \
    alsa-lib-devel \
    v4l-utils \
    libatomic \
    cmake

# Instalar herramientas para Arduino (opcional)
print_info "Instalando herramientas para Arduino..."
sudo dnf install -y arduino-core arduino-ide || print_warn "Arduino IDE no disponible en repositorios"

# ============================================
# 2. Configurar entorno Python virtual
# ============================================
print_info "Creando entorno virtual Python..."

python3 -m venv venv
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# ============================================
# 3. Instalar dependencias Python
# ============================================
print_info "Instalando dependencias de Python..."

pip install -r requirements.txt

# ============================================
# 4. Instalar Ollama (si no está instalado)
# ============================================
if ! command -v ollama &> /dev/null; then
    print_info "Instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    print_info "Ollama instalado correctamente"
else
    print_info "Ollama ya está instalado"
fi

# ============================================
# 5. Descargar modelos de IA
# ============================================
print_info "Descargando modelo Gemma 4..."

# Iniciar Ollama en segundo plano
ollama serve &
OLLAMA_PID=$!
sleep 5

# Pull del modelo principal
ollama pull gemma4:4b-instruct-q4_K_M || print_warn "Error descargando Gemma 4, verificar nombre del modelo"

# Detener Ollama temporalmente
kill $OLLAMA_PID 2>/dev/null || true

# ============================================
# 6. Configurar voces Piper TTS
# ============================================
print_info "Configurando Piper TTS..."

mkdir -p data/piper_voices

# Descargar voz en español (ejemplo: carlfm)
if [ ! -f "data/piper_voices/es_ES-carlfm-medium.onnx" ]; then
    print_info "Descargando voz en español para Piper..."
    
    # URLs de ejemplo (verificar las actuales en https://github.com/rhasspy/piper)
    wget -O data/piper_voices/es_ES-carlfm-medium.onnx \
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx" || \
    print_warn "No se pudo descargar la voz automáticamente. Descargar manualmente de piper-voices"
    
    wget -O data/piper_voices/es_ES-carlfm-medium.onnx.json \
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/medium/es_ES-carlfm-medium.onnx.json" || true
fi

# ============================================
# 7. Configurar permisos de hardware
# ============================================
print_info "Configurando permisos de hardware..."

# Añadir usuario al grupo dialout (para acceso serial a Arduino)
sudo usermod -a -G dialout $USER

# Crear regla udev para Arduino (opcional pero recomendado)
cat << 'EOF' | sudo tee /etc/udev/rules.d/99-arduino.rules > /dev/null
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="2a03", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

# ============================================
# 8. Crear directorios necesarios
# ============================================
print_info "Creando estructura de directorios..."

mkdir -p data logs tests

# ============================================
# 9. Compilar firmware Arduino (opcional)
# ============================================
print_info "Compilando firmware Arduino..."

if command -v arduino-cli &> /dev/null; then
    cd src/hardware/arduino_firmware
    
    # Configurar board
    arduino-cli config init
    arduino-cli core update-index
    arduino-cli core install arduino:avr
    
    # Compilar
    arduino-cli compile --fqbn arduino:avr:nano ir_button_controller.ino
    
    cd ../../..
    print_info "Firmware compilado correctamente"
else
    print_warn "arduino-cli no encontrado. Compilar firmware manualmente desde Arduino IDE"
fi

# ============================================
# 10. Crear servicio systemd (opcional)
# ============================================
print_info "Creando servicio systemd para inicio automático..."

cat << EOF | sudo tee /etc/systemd/system/abuelo-ia.service > /dev/null
[Unit]
Description=Abuelo IA Assistant
After=network.target sound.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:$PATH"
ExecStart=$(pwd)/venv/bin/python -m src.agent.abuelo_agent
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
print_info "Servicio creado. Para iniciar: sudo systemctl start abuelo-ia"
print_info "Para autoinicio: sudo systemctl enable abuelo-ia"

# ============================================
# Resumen final
# ============================================
echo ""
echo "=================================================="
print_info "¡Instalación completada!"
echo ""
echo "Próximos pasos:"
echo "  1. Conectar el Arduino y cargar el firmware (src/hardware/arduino_firmware/)"
echo "  2. Configurar el puerto serial en config/settings.yaml"
echo "  3. Probar el sistema: source venv/bin/activate && python -m src.agent.abuelo_agent"
echo "  4. (Opcional) Habilitar servicio: sudo systemctl enable abuelo-ia"
echo ""
echo "Documentación completa en: docs/"
echo "=================================================="
